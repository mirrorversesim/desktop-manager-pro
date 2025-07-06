import win32gui
import win32con
import win32api
import win32process
from typing import Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """Manager class for window operations"""
    
    def __init__(self):
        self.logger = logger
    
    def minimize_window(self, hwnd: int) -> bool:
        """Minimize a window."""
        return minimize_window(hwnd)
    
    def maximize_window(self, hwnd: int) -> bool:
        """Maximize a window."""
        return maximize_window(hwnd)
    
    def restore_window(self, hwnd: int) -> bool:
        """Restore a window from minimized or maximized state."""
        return restore_window(hwnd)
    
    def close_window(self, hwnd: int) -> bool:
        """Send WM_CLOSE message to request a window to close gracefully."""
        return close_window(hwnd)
    
    def bring_to_foreground(self, hwnd: int) -> bool:
        """Bring a window to the foreground and activate it."""
        return bring_to_foreground(hwnd)
    
    def is_window_visible(self, hwnd: int) -> bool:
        """Check if a window is visible."""
        return is_window_visible(hwnd)
    
    def get_window_state(self, hwnd: int) -> int:
        """Get the current state of a window."""
        return get_window_state(hwnd)
    
    def get_window_title(self, hwnd: int) -> str:
        """Get the title of a window."""
        return get_window_title(hwnd)
    
    def get_window_class(self, hwnd: int) -> str:
        """Get the class name of a window."""
        return get_window_class(hwnd)
    
    def get_window_process_id(self, hwnd: int) -> Optional[int]:
        """Get the process ID of a window."""
        return get_window_process_id(hwnd)
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Get the position and size of a window."""
        return get_window_rect(hwnd)
    
    def set_window_pos(self, hwnd: int, x: int, y: int, width: int, height: int, flags: int = 0) -> bool:
        """Set the position and size of a window."""
        return set_window_pos(hwnd, x, y, width, height, flags)
    
    def is_window_top_level(self, hwnd: int) -> bool:
        """Check if a window is a top-level window."""
        return is_window_top_level(hwnd)
    
    def hide_window(self, hwnd: int) -> bool:
        """Hide a window."""
        return hide_window(hwnd)
    
    def show_window(self, hwnd: int) -> bool:
        """Show a window."""
        return show_window(hwnd)
    
    def flash_window(self, hwnd: int, count: int = 3) -> bool:
        """Flash a window to draw attention."""
        return flash_window(hwnd, count)


def minimize_window(hwnd: int) -> bool:
    """
    Minimize a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        if result:
            logger.debug(f"Minimized window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to minimize window {hwnd}: {e}")
        return False


def maximize_window(hwnd: int) -> bool:
    """
    Maximize a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        if result:
            logger.debug(f"Maximized window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to maximize window {hwnd}: {e}")
        return False


def restore_window(hwnd: int) -> bool:
    """
    Restore a window from minimized or maximized state.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        if result:
            logger.debug(f"Restored window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to restore window {hwnd}: {e}")
        return False


def close_window(hwnd: int) -> bool:
    """
    Send WM_CLOSE message to request a window to close gracefully.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if message was sent successfully
    """
    try:
        result = win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        if result:
            logger.debug(f"Sent close message to window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to close window {hwnd}: {e}")
        return False


def bring_to_foreground(hwnd: int) -> bool:
    """
    Bring a window to the foreground and activate it.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        # First, restore the window if it's minimized
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
        # Bring to foreground
        result = win32gui.SetForegroundWindow(hwnd)
        if result:
            logger.debug(f"Brought window {hwnd} to foreground")
        return result
    except Exception as e:
        logger.error(f"Failed to bring window {hwnd} to foreground: {e}")
        return False


def is_window_visible(hwnd: int) -> bool:
    """
    Check if a window is visible.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if window is visible
    """
    try:
        return win32gui.IsWindowVisible(hwnd)
    except Exception as e:
        logger.warning(f"Failed to check visibility for window {hwnd}: {e}")
        return False


def get_window_state(hwnd: int) -> int:
    """
    Get the current state of a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        int: Window state (SW_SHOWNORMAL, SW_MINIMIZE, SW_MAXIMIZE, etc.)
    """
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        return placement[1]  # Current state
    except Exception as e:
        logger.warning(f"Failed to get window state for {hwnd}: {e}")
        return win32con.SW_SHOWNORMAL


def get_window_title(hwnd: int) -> str:
    """
    Get the title of a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        str: Window title
    """
    try:
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        logger.warning(f"Failed to get title for window {hwnd}: {e}")
        return ""


def get_window_class(hwnd: int) -> str:
    """
    Get the class name of a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        str: Window class name
    """
    try:
        return win32gui.GetClassName(hwnd)
    except Exception as e:
        logger.warning(f"Failed to get class for window {hwnd}: {e}")
        return ""


def get_window_process_id(hwnd: int) -> Optional[int]:
    """
    Get the process ID of a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        int: Process ID or None if failed
    """
    try:
        return win32process.GetWindowThreadProcessId(hwnd)[1]
    except Exception as e:
        logger.warning(f"Failed to get PID for window {hwnd}: {e}")
        return None


def get_window_rect(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Get the position and size of a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        Tuple: (left, top, right, bottom) or None if failed
    """
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception as e:
        logger.warning(f"Failed to get rect for window {hwnd}: {e}")
        return None


def set_window_pos(hwnd: int, x: int, y: int, width: int, height: int, flags: int = 0) -> bool:
    """
    Set the position and size of a window.
    
    Args:
        hwnd (int): Window handle
        x (int): X position
        y (int): Y position
        width (int): Window width
        height (int): Window height
        flags (int): SWP flags (default: 0)
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.SetWindowPos(hwnd, 0, x, y, width, height, flags)
        if result:
            logger.debug(f"Set position for window {hwnd} to ({x}, {y}, {width}, {height})")
        return result
    except Exception as e:
        logger.error(f"Failed to set position for window {hwnd}: {e}")
        return False


def is_window_top_level(hwnd: int) -> bool:
    """
    Check if a window is a top-level window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if window is top-level
    """
    try:
        return win32gui.GetParent(hwnd) == 0
    except Exception as e:
        logger.warning(f"Failed to check if window {hwnd} is top-level: {e}")
        return False


def hide_window(hwnd: int) -> bool:
    """
    Hide a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        if result:
            logger.debug(f"Hidden window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to hide window {hwnd}: {e}")
        return False


def show_window(hwnd: int) -> bool:
    """
    Show a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        if result:
            logger.debug(f"Shown window {hwnd}")
        return result
    except Exception as e:
        logger.error(f"Failed to show window {hwnd}: {e}")
        return False


def flash_window(hwnd: int, count: int = 3) -> bool:
    """
    Flash a window to draw attention to it.
    
    Args:
        hwnd (int): Window handle
        count (int): Number of flashes
        
    Returns:
        bool: True if successful
    """
    try:
        result = win32gui.FlashWindow(hwnd, True)
        if result:
            logger.debug(f"Flashed window {hwnd} {count} times")
        return result
    except Exception as e:
        logger.error(f"Failed to flash window {hwnd}: {e}")
        return False 