import os
from typing import List, Dict, Any, Optional
from ..core.window_manager import (
    minimize_window, close_window, bring_to_foreground,
    is_window_visible, is_window_top_level
)
from ..utils.win32_helpers import get_explorer_folder_path, get_window_process_name, enum_explorer_windows_with_paths
from ..utils.logger import get_logger

logger = get_logger(__name__)


def perform_action(action_type: str, target_windows: List[Dict[str, Any]], 
                  new_window_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    Central function that dispatches to specific helper functions based on action_type.
    
    Args:
        action_type: Type of action to perform
        target_windows: List of window info dictionaries to act upon
        new_window_info: Information about the triggering window (optional)
        
    Returns:
        bool: True if action was performed successfully
    """
    try:
        logger.info(f"Performing action: {action_type} on {len(target_windows)} windows")
        
        if action_type == "MINIMIZE_OTHERS_OF_SAME_APP":
            return _minimize_others_of_same_app(target_windows, new_window_info)
        elif action_type == "CLOSE_DUPLICATE_PATH":
            return _close_duplicate_path(target_windows, new_window_info)
        elif action_type == "BRING_TO_FOREGROUND":
            return _bring_to_foreground(target_windows)
        elif action_type == "CLOSE_WINDOW":
            return _close_windows(target_windows)
        elif action_type == "HIDE_WINDOW":
            return _hide_windows(target_windows)
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error performing action {action_type}: {e}")
        return False


def _minimize_others_of_same_app(target_windows: List[Dict[str, Any]], 
                                new_window_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    Minimize other windows of the same application.
    
    Args:
        target_windows: List of window info dictionaries
        new_window_info: Information about the new window that triggered the action
        
    Returns:
        bool: True if action was performed successfully
    """
    try:
        if not new_window_info:
            logger.warning("No new window info provided for MINIMIZE_OTHERS_OF_SAME_APP")
            return False
            
        new_window_hwnd = new_window_info.get('hwnd')
        new_window_exe = new_window_info.get('exe_path', '')
        
        if not new_window_exe:
            logger.warning("No executable path found for new window")
            return False
            
        # Extract executable name from path
        new_exe_name = os.path.basename(new_window_exe).lower()
        
        minimized_count = 0
        for window_info in target_windows:
            hwnd = window_info.get('hwnd')
            
            # Skip the triggering window
            if hwnd == new_window_hwnd:
                continue
                
            # Check if it's the same application
            window_exe = window_info.get('exe_path', '')
            if window_exe:
                window_exe_name = os.path.basename(window_exe).lower()
                if window_exe_name == new_exe_name:
                    # Check if window is visible and top-level
                    if (window_info.get('is_visible', False) and 
                        window_info.get('is_top_level', False)):
                        
                        if minimize_window(hwnd):
                            minimized_count += 1
                            logger.info(f"Minimized window: {window_info.get('title', 'Unknown')} (HWND: {hwnd})")
                        else:
                            logger.warning(f"Failed to minimize window {hwnd}")
        
        logger.info(f"Minimized {minimized_count} windows of {new_exe_name}")
        return minimized_count > 0
        
    except Exception as e:
        logger.error(f"Error in _minimize_others_of_same_app: {e}")
        return False


def _close_duplicate_path(target_windows: List[Dict[str, Any]], 
                         new_window_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    Close windows that have the same folder path (for explorer windows),
    but keep the newest/foreground window open and close the older/background one.
    """
    try:
        if not new_window_info:
            logger.warning("No new window info provided for CLOSE_DUPLICATE_PATH")
            return False
        new_window_hwnd = new_window_info.get('hwnd')
        new_window_class = new_window_info.get('class_name', '')
        if new_window_class != "CabinetWClass":
            logger.debug("Not an explorer window, skipping duplicate path check")
            return False
        new_window_path = get_explorer_folder_path(new_window_hwnd)
        if not new_window_path:
            logger.warning("Could not determine folder path for new explorer window")
            return False
        logger.info(f"New explorer window opened to: {new_window_path}")
        explorer_windows = enum_explorer_windows_with_paths()
        # Find all windows with the same path (including the new one)
        duplicates = [win for win in explorer_windows if win['path'].lower() == new_window_path.lower()]
        if len(duplicates) <= 1:
            logger.info("No duplicates found for this folder window.")
            return False
        # Try to identify the new window (foreground or highest Z-order)
        import win32gui
        foreground_hwnd = win32gui.GetForegroundWindow()
        # Prefer to keep the new window (by hwnd), or the foreground window if not sure
        keep_hwnd = new_window_hwnd if new_window_hwnd in [d['hwnd'] for d in duplicates] else foreground_hwnd
        closed_count = 0
        for win in duplicates:
            hwnd = win['hwnd']
            if hwnd == keep_hwnd:
                continue  # Don't close the new/foreground window
            if close_window(hwnd):
                closed_count += 1
                logger.info(f"Closed duplicate explorer window: {win['path']} (HWND: {hwnd})")
            else:
                logger.warning(f"Failed to close duplicate window {hwnd}")
        # Optionally, bring the kept window to the foreground
        try:
            from ..core.window_manager import bring_to_foreground
            bring_to_foreground(keep_hwnd)
        except Exception:
            pass
        logger.info(f"Closed {closed_count} duplicate explorer windows (kept HWND: {keep_hwnd})")
        return closed_count > 0
    except Exception as e:
        logger.error(f"Error in _close_duplicate_path: {e}")
        return False


def _bring_to_foreground(target_windows: List[Dict[str, Any]]) -> bool:
    """
    Bring windows to the foreground.
    
    Args:
        target_windows: List of window info dictionaries
        
    Returns:
        bool: True if action was performed successfully
    """
    try:
        success_count = 0
        for window_info in target_windows:
            hwnd = window_info.get('hwnd')
            
            if bring_to_foreground(hwnd):
                success_count += 1
                logger.info(f"Brought to foreground: {window_info.get('title', 'Unknown')} (HWND: {hwnd})")
            else:
                logger.warning(f"Failed to bring window {hwnd} to foreground")
        
        logger.info(f"Brought {success_count} windows to foreground")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error in _bring_to_foreground: {e}")
        return False


def _close_windows(target_windows: List[Dict[str, Any]]) -> bool:
    """
    Close windows.
    
    Args:
        target_windows: List of window info dictionaries
        
    Returns:
        bool: True if action was performed successfully
    """
    try:
        closed_count = 0
        for window_info in target_windows:
            hwnd = window_info.get('hwnd')
            
            if close_window(hwnd):
                closed_count += 1
                logger.info(f"Closed window: {window_info.get('title', 'Unknown')} (HWND: {hwnd})")
            else:
                logger.warning(f"Failed to close window {hwnd}")
        
        logger.info(f"Closed {closed_count} windows")
        return closed_count > 0
        
    except Exception as e:
        logger.error(f"Error in _close_windows: {e}")
        return False


def _hide_windows(target_windows: List[Dict[str, Any]]) -> bool:
    """
    Hide windows.
    
    Args:
        target_windows: List of window info dictionaries
        
    Returns:
        bool: True if action was performed successfully
    """
    try:
        from ..core.window_manager import hide_window
        
        hidden_count = 0
        for window_info in target_windows:
            hwnd = window_info.get('hwnd')
            
            if hide_window(hwnd):
                hidden_count += 1
                logger.info(f"Hidden window: {window_info.get('title', 'Unknown')} (HWND: {hwnd})")
            else:
                logger.warning(f"Failed to hide window {hwnd}")
        
        logger.info(f"Hidden {hidden_count} windows")
        return hidden_count > 0
        
    except Exception as e:
        logger.error(f"Error in _hide_windows: {e}")
        return False


def get_supported_actions() -> List[str]:
    """
    Get a list of supported action types.
    
    Returns:
        List[str]: List of supported action types
    """
    return [
        "MINIMIZE_OTHERS_OF_SAME_APP",
        "CLOSE_DUPLICATE_PATH", 
        "BRING_TO_FOREGROUND",
        "CLOSE_WINDOW",
        "HIDE_WINDOW"
    ] 