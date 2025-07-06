import threading
import time
import os
from typing import Dict, Any, List, Optional
from collections import defaultdict
import win32con
from ..utils.logger import get_logger
from ..utils.win32_helpers import enum_top_level_windows, get_window_info
from .actions import perform_action
from .config import get_enabled_rules, sort_rules_by_priority

logger = get_logger(__name__)


class RuleEngine:
    """
    Core logic for evaluating rules against incoming events.
    """
    
    def __init__(self, rules_config: List[Dict[str, Any]]):
        """
        Initialize the rule engine.
        
        Args:
            rules_config: List of rule configurations
        """
        self.rules_config = rules_config
        self._internal_window_state: Dict[int, Dict[str, Any]] = {}
        self._window_state_lock = threading.Lock()
        self._event_count = 0
        self._rule_execution_count = defaultdict(int)
        
        # Event type mapping
        self.event_type_mapping = {
            win32con.EVENT_OBJECT_CREATE: "CREATE",
            win32con.EVENT_OBJECT_DESTROY: "DESTROY",
            win32con.EVENT_OBJECT_SHOW: "SHOW",
            win32con.EVENT_OBJECT_HIDE: "HIDE",
            win32con.EVENT_SYSTEM_FOREGROUND: "FOREGROUND",
            win32con.EVENT_OBJECT_NAMECHANGE: "NAMECHANGE"
        }
        
        logger.info(f"RuleEngine initialized with {len(rules_config)} rules")
        
        # Initialize window state with currently open windows
        self._initialize_window_state()
    
    def _initialize_window_state(self):
        """Initialize the internal window state with currently open windows."""
        try:
            logger.info("Initializing window state with currently open windows...")
            
            with self._window_state_lock:
                for hwnd in enum_top_level_windows():
                    window_info = get_window_info(hwnd)
                    if window_info and window_info.get('title'):
                        self._internal_window_state[hwnd] = window_info
                        
            logger.info(f"Initialized window state with {len(self._internal_window_state)} windows")
            
        except Exception as e:
            logger.error(f"Error initializing window state: {e}")
    
    def process_event(self, event_id: int, hwnd: int, window_info: Dict[str, Any]) -> None:
        """
        Process an incoming event from the EventMonitor.
        
        Args:
            event_id: Windows event ID
            hwnd: Window handle
            window_info: Window information dictionary
        """
        try:
            self._event_count += 1
            
            # Map event ID to event type
            event_type = self.event_type_mapping.get(event_id, f"UNKNOWN_{event_id}")
            
            logger.debug(f"Processing event {event_type} for window {window_info.get('title', 'Unknown')} (HWND: {hwnd})")
            
            # Update internal window state
            self._update_window_state(event_type, hwnd, window_info)
            
            # Get enabled rules sorted by priority
            enabled_rules = get_enabled_rules(self.rules_config)
            sorted_rules = sort_rules_by_priority(enabled_rules)
            
            # Evaluate rules
            for rule in sorted_rules:
                if self._match_rule_condition(rule, event_type, window_info):
                    logger.info(f"Rule '{rule['name']}' matched for event {event_type}")
                    
                    # Get target windows for the action
                    target_windows = self._filter_target_windows(rule, window_info)
                    
                    if target_windows:
                        # Execute the action
                        action_type = rule['action']['type']
                        success = perform_action(action_type, target_windows, window_info)
                        
                        if success:
                            self._rule_execution_count[rule['name']] += 1
                            logger.info(f"Successfully executed rule '{rule['name']}' on {len(target_windows)} windows")
                        else:
                            logger.warning(f"Failed to execute rule '{rule['name']}'")
                    else:
                        logger.debug(f"Rule '{rule['name']}' matched but no target windows found")
                        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    def _update_window_state(self, event_type: str, hwnd: int, window_info: Dict[str, Any]) -> None:
        """
        Update the internal window state based on the event.
        
        Args:
            event_type: Type of event (CREATE, DESTROY, etc.)
            hwnd: Window handle
            window_info: Window information
        """
        with self._window_state_lock:
            if event_type == "CREATE" or event_type == "SHOW":
                # Add or update window in state
                self._internal_window_state[hwnd] = window_info
                logger.debug(f"Added/updated window {hwnd} in state")
                
            elif event_type == "DESTROY" or event_type == "HIDE":
                # Remove window from state
                if hwnd in self._internal_window_state:
                    del self._internal_window_state[hwnd]
                    logger.debug(f"Removed window {hwnd} from state")
                    
            elif event_type == "NAMECHANGE":
                # Update window information
                if hwnd in self._internal_window_state:
                    self._internal_window_state[hwnd].update(window_info)
                    logger.debug(f"Updated window {hwnd} information")
    
    def _match_rule_condition(self, rule: Dict[str, Any], event_type: str, 
                            window_info: Dict[str, Any]) -> bool:
        """
        Check if a window and event match a rule's trigger condition.
        
        Args:
            rule: Rule configuration
            event_type: Type of event
            window_info: Window information
            
        Returns:
            bool: True if the rule condition is matched
        """
        try:
            trigger = rule.get('trigger', {})
            
            # Check event type
            if trigger.get('event_type') != event_type:
                return False
            
            # Check executable name if specified
            if 'executable_name' in trigger:
                expected_exe = trigger['executable_name'].lower()
                window_exe = window_info.get('exe_path', '')
                if window_exe:
                    actual_exe = os.path.basename(window_exe).lower()
                    if actual_exe != expected_exe:
                        return False
                else:
                    return False
            
            # Check window class if specified
            if 'window_class' in trigger:
                expected_class = trigger['window_class']
                actual_class = window_info.get('class_name', '')
                if actual_class != expected_class:
                    return False
            
            # Check window title pattern if specified
            if 'title_pattern' in trigger:
                import re
                pattern = trigger['title_pattern']
                title = window_info.get('title', '')
                if not re.search(pattern, title):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching rule condition: {e}")
            return False
    
    def _filter_target_windows(self, rule: Dict[str, Any], 
                             new_window_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter windows based on the rule's action target filter.
        
        Args:
            rule: Rule configuration
            new_window_info: Information about the triggering window
            
        Returns:
            List[Dict[str, Any]]: List of target windows
        """
        try:
            action = rule.get('action', {})
            target_windows = []
            
            with self._window_state_lock:
                for hwnd, window_info in self._internal_window_state.items():
                    # Skip the triggering window if specified
                    if action.get('exclude_trigger_window', False):
                        if hwnd == new_window_info.get('hwnd'):
                            continue
                    
                    # Check if window should be included based on filters
                    if self._window_matches_filter(window_info, action):
                        target_windows.append(window_info)
            
            return target_windows
            
        except Exception as e:
            logger.error(f"Error filtering target windows: {e}")
            return []
    
    def _window_matches_filter(self, window_info: Dict[str, Any], 
                             action: Dict[str, Any]) -> bool:
        """
        Check if a window matches the action's target filter.
        
        Args:
            window_info: Window information
            action: Action configuration
            
        Returns:
            bool: True if window matches the filter
        """
        try:
            # Check visibility requirement
            if action.get('is_visible', False):
                if not window_info.get('is_visible', False):
                    return False
            
            # Check top-level requirement
            if action.get('is_top_level', False):
                if not window_info.get('is_top_level', False):
                    return False
            
            # Check same executable requirement
            if action.get('same_executable', False):
                # This would need to be implemented based on the triggering window
                # For now, we'll skip this check as it requires context
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking window filter: {e}")
            return False
    
    def get_window_state(self) -> Dict[int, Dict[str, Any]]:
        """
        Get a copy of the current window state.
        
        Returns:
            Dict[int, Dict[str, Any]]: Copy of window state
        """
        with self._window_state_lock:
            return self._internal_window_state.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about rule engine operation.
        
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        with self._window_state_lock:
            return {
                'total_events_processed': self._event_count,
                'current_windows_tracked': len(self._internal_window_state),
                'rule_execution_counts': dict(self._rule_execution_count),
                'enabled_rules': len(get_enabled_rules(self.rules_config))
            }
    
    def refresh_window_state(self) -> None:
        """
        Refresh the window state by re-enumerating all windows.
        """
        try:
            logger.info("Refreshing window state...")
            self._initialize_window_state()
        except Exception as e:
            logger.error(f"Error refreshing window state: {e}")
    
    def clear_statistics(self) -> None:
        """Clear execution statistics."""
        self._event_count = 0
        self._rule_execution_count.clear()
        logger.info("Statistics cleared") 