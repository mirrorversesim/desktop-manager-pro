import threading
import time
import win32gui
import win32con
import win32api
import pythoncom
from typing import Callable, Optional, Dict, Any
from ..utils.logger import get_logger
from ..utils.win32_helpers import get_window_info, is_system_window

logger = get_logger(__name__)


class EventMonitor:
    """
    Core event listener responsible for setting up Windows event hooks and running the message loop.
    """
    
    def __init__(self, event_callback: Callable[[int, int, Dict[str, Any]], None]):
        """
        Initialize the event monitor.
        
        Args:
            event_callback: Function to call when events occur. 
                          Signature: callback(event_id, hwnd, window_info)
        """
        self.event_callback = event_callback
        self.monitoring_thread: Optional[threading.Thread] = None
        self.thread_id: Optional[int] = None
        self.hook_handle: Optional[int] = None
        self.running = False
        self.polling_interval = 3.0  # Default polling interval
        self.interval_lock = threading.Lock()  # Thread-safe interval changes
        
        # Event type mapping
        self.event_types = {
            win32con.EVENT_OBJECT_CREATE: "CREATE",
            win32con.EVENT_OBJECT_DESTROY: "DESTROY",
            win32con.EVENT_OBJECT_SHOW: "SHOW",
            win32con.EVENT_OBJECT_HIDE: "HIDE",
            win32con.EVENT_SYSTEM_FOREGROUND: "FOREGROUND",
            win32con.EVENT_OBJECT_NAMECHANGE: "NAMECHANGE",
            win32con.EVENT_OBJECT_FOCUS: "FOCUS",
            win32con.EVENT_OBJECT_VALUECHANGE: "VALUECHANGE"
        }
        
        logger.info("EventMonitor initialized")
    
    def _event_hook_callback(self, hWinEventHook: int, event: int, hwnd: int, 
                           idObject: int, idChild: int, dwEventThread: int, 
                           dwmsEventTime: int) -> None:
        """
        Static method that SetWinEventHook calls when events occur.
        
        Args:
            hWinEventHook: Handle to the event hook
            event: Event type
            hwnd: Window handle
            idObject: Object identifier
            idChild: Child identifier
            dwEventThread: Thread ID
            dwmsEventTime: Event time
        """
        try:
            # Filter out system windows and invalid handles
            if not hwnd or is_system_window(hwnd):
                return
                
            # Get event type name
            event_name = self.event_types.get(event, f"UNKNOWN_{event}")
            
            # Get window information
            window_info = get_window_info(hwnd)
            
            # Log the event (debug level to avoid spam)
            logger.debug(f"Event: {event_name} - Window: {window_info.get('title', 'Unknown')} "
                        f"(HWND: {hwnd}, Class: {window_info.get('class_name', 'Unknown')})")
            
            # Call the event callback
            self.event_callback(event, hwnd, window_info)
            
        except Exception as e:
            logger.error(f"Error in event hook callback: {e}")
    
    def _run_message_loop(self) -> None:
        """
        Method to be executed in the dedicated monitoring thread.
        Uses optimized polling-based monitoring with differential updates.
        """
        try:
            # Initialize COM for this thread
            pythoncom.CoInitialize()
            logger.debug("COM initialized for monitoring thread")
            
            # Store the thread ID
            self.thread_id = win32api.GetCurrentThreadId()
            logger.info(f"Monitoring thread started with ID: {self.thread_id}")
            
            logger.info("Starting optimized polling-based window monitoring...")
            
            # Track previous window state with more detail
            previous_windows = {}  # hwnd -> basic_info (title, class_name)
            
            # Polling loop
            while self.running:
                try:
                    # Get current windows efficiently
                    current_windows = {}
                    windows_list = []
                    
                    # Use EnumWindows with a more efficient callback
                    def enum_callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd) and win32gui.GetParent(hwnd) == 0:
                            if not is_system_window(hwnd):
                                # Get basic info only (avoid expensive operations)
                                try:
                                    title = win32gui.GetWindowText(hwnd)
                                    class_name = win32gui.GetClassName(hwnd)
                                    if title:  # Only track windows with titles
                                        windows[hwnd] = {
                                            'hwnd': hwnd,
                                            'title': title,
                                            'class_name': class_name
                                        }
                                except Exception:
                                    pass  # Skip problematic windows
                    
                    win32gui.EnumWindows(enum_callback, current_windows)
                    
                    # Differential update - only process changes
                    new_windows = set(current_windows.keys()) - set(previous_windows.keys())
                    closed_windows = set(previous_windows.keys()) - set(current_windows.keys())
                    changed_windows = set()
                    
                    # Check for title changes in existing windows
                    for hwnd in set(current_windows.keys()) & set(previous_windows.keys()):
                        if (current_windows[hwnd]['title'] != previous_windows[hwnd]['title'] or
                            current_windows[hwnd]['class_name'] != previous_windows[hwnd]['class_name']):
                            changed_windows.add(hwnd)
                    
                    # Process new windows (with full info only when needed)
                    for hwnd in new_windows:
                        logger.debug(f"Detected new window: {current_windows[hwnd]['title']} (HWND: {hwnd})")
                        # Get full window info only when we detect a new window
                        window_info = get_window_info(hwnd)
                        if window_info:
                            self.event_callback(win32con.EVENT_OBJECT_CREATE, hwnd, window_info)
                    
                    # Process closed windows
                    for hwnd in closed_windows:
                        logger.debug(f"Detected closed window (HWND: {hwnd})")
                        # Create minimal window info for closed window
                        window_info = {
                            'hwnd': hwnd, 
                            'title': previous_windows[hwnd]['title'], 
                            'class_name': previous_windows[hwnd]['class_name'], 
                            'pid': None, 
                            'exe_path': None, 
                            'is_visible': False, 
                            'is_top_level': False, 
                            'window_state': win32con.SW_SHOWNORMAL
                        }
                        self.event_callback(win32con.EVENT_OBJECT_DESTROY, hwnd, window_info)
                    
                    # Process changed windows
                    for hwnd in changed_windows:
                        logger.debug(f"Detected changed window: {current_windows[hwnd]['title']} (HWND: {hwnd})")
                        # Get full window info for changed windows
                        window_info = get_window_info(hwnd)
                        if window_info:
                            self.event_callback(win32con.EVENT_OBJECT_NAMECHANGE, hwnd, window_info)
                    
                    # Update previous state
                    previous_windows = current_windows.copy()
                    
                    # Sleep to avoid excessive CPU usage (thread-safe interval)
                    with self.interval_lock:
                        current_interval = self.polling_interval
                    time.sleep(current_interval)
                    
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    time.sleep(5)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Error in monitoring thread: {e}")
        finally:
            # Cleanup
            try:
                pythoncom.CoUninitialize()
                logger.debug("COM uninitialized")
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            
            self.running = False
            logger.info("Monitoring thread stopped")
    
    def start(self) -> bool:
        """
        Start the event monitoring in a dedicated thread.
        
        Returns:
            bool: True if started successfully
        """
        if self.running:
            logger.warning("Event monitor is already running")
            return False
            
        try:
            # Create and start the monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._run_message_loop,
                daemon=True,
                name="EventMonitor"
            )
            
            self.monitoring_thread.start()
            self.running = True
            
            # Wait a moment to ensure the thread starts
            time.sleep(0.1)
            
            if self.monitoring_thread.is_alive():
                logger.info("Event monitor started successfully")
                return True
            else:
                logger.error("Failed to start monitoring thread")
                self.running = False
                return False
                
        except Exception as e:
            logger.error(f"Error starting event monitor: {e}")
            self.running = False
            return False
    
    def stop(self) -> bool:
        """
        Stop the event monitoring gracefully.
        
        Returns:
            bool: True if stopped successfully
        """
        if not self.running:
            logger.warning("Event monitor is not running")
            return False
            
        try:
            logger.info("Stopping event monitor...")
            
            # Set running flag to False to stop the polling loop
            self.running = False
            
            # Wait for the thread to finish (with timeout)
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5.0)
                
                if self.monitoring_thread.is_alive():
                    logger.warning("Monitoring thread did not stop gracefully")
                    return False
            
            logger.info("Event monitor stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping event monitor: {e}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if the event monitor is currently running.
        
        Returns:
            bool: True if running
        """
        return self.running and (self.monitoring_thread and self.monitoring_thread.is_alive())
    
    def set_polling_interval(self, interval: float) -> bool:
        """
        Change the polling interval dynamically.
        
        Args:
            interval (float): New polling interval in seconds
            
        Returns:
            bool: True if interval was set successfully
        """
        if interval < 0.1:
            logger.warning("Polling interval too low, setting to 0.1 seconds")
            interval = 0.1
        elif interval > 60.0:
            logger.warning("Polling interval too high, setting to 60 seconds")
            interval = 60.0
            
        with self.interval_lock:
            old_interval = self.polling_interval
            self.polling_interval = interval
            
        logger.info(f"Polling interval changed from {old_interval}s to {interval}s")
        return True
    
    def get_polling_interval(self) -> float:
        """
        Get the current polling interval.
        
        Returns:
            float: Current polling interval in seconds
        """
        with self.interval_lock:
            return self.polling_interval
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the event monitor.
        
        Returns:
            dict: Status information
        """
        return {
            'running': self.running,
            'thread_alive': self.monitoring_thread.is_alive() if self.monitoring_thread else False,
            'thread_id': self.thread_id,
            'hook_handle': self.hook_handle,
            'polling_interval': self.get_polling_interval()
        } 