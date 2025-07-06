import os
import sys
import urllib.parse
from typing import Optional, Dict, Any, Generator
import win32gui
import win32process
import win32api
import win32con
import psutil
import pythoncom
import win32com.client
from .logger import get_logger
from .cache import cached_executable_path, cached_folder_path, cached_window_info

logger = get_logger(__name__)


@cached_window_info
def get_window_info(hwnd: int) -> Dict[str, Any]:
    """
    Get comprehensive information about a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        Dict containing window details: hwnd, title, class_name, pid, exe_path, is_visible, is_top_level
    """
    try:
        # Basic window information
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        # Process information
        try:
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        except Exception as e:
            logger.warning(f"Failed to get PID for window {hwnd}: {e}")
            pid = None
            
        # Executable path
        exe_path = None
        if pid:
            exe_path = get_executable_path_from_pid(pid)
            
        # Window state
        is_visible = win32gui.IsWindowVisible(hwnd)
        is_top_level = (win32gui.GetParent(hwnd) == 0)
        
        # Get window placement for state information
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            window_state = placement[1]  # SW_SHOWNORMAL, SW_MINIMIZE, etc.
        except Exception as e:
            logger.warning(f"Failed to get window placement for {hwnd}: {e}")
            window_state = win32con.SW_SHOWNORMAL
            
        return {
            'hwnd': hwnd,
            'title': title,
            'class_name': class_name,
            'pid': pid,
            'exe_path': exe_path,
            'is_visible': is_visible,
            'is_top_level': is_top_level,
            'window_state': window_state
        }
        
    except Exception as e:
        logger.error(f"Error getting window info for {hwnd}: {e}")
        return {
            'hwnd': hwnd,
            'title': '',
            'class_name': '',
            'pid': None,
            'exe_path': None,
            'is_visible': False,
            'is_top_level': False,
            'window_state': win32con.SW_SHOWNORMAL
        }


@cached_executable_path
def get_executable_path_from_pid(pid: int) -> Optional[str]:
    """
    Get executable path from process ID using win32process or psutil.
    
    Args:
        pid (int): Process ID
        
    Returns:
        str: Executable path or None if failed
    """
    try:
        # Try using psutil first (more robust)
        process = psutil.Process(pid)
        return process.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        try:
            # Fallback to win32process
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False, pid
            )
            try:
                exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
                return exe_path
            finally:
                win32api.CloseHandle(process_handle)
        except Exception as e:
            logger.warning(f"Failed to get executable path for PID {pid}: {e}")
            return None


@cached_folder_path
def get_explorer_folder_path(hwnd: int) -> Optional[str]:
    """
    Get the canonical folder path for an explorer.exe window using Shell.Application COM object.
    
    Args:
        hwnd (int): Window handle of explorer window
        
    Returns:
        str: Canonical folder path or None if not found
    """
    try:
        # Check if this is an explorer window
        class_name = win32gui.GetClassName(hwnd)
        if class_name != "CabinetWClass":
            return None
            
        # Initialize COM if not already done
        try:
            pythoncom.CoInitialize()
        except pythoncom.com_error:
            # COM already initialized
            pass
            
        try:
            # Get Shell.Application object
            shell = win32com.client.Dispatch("Shell.Application")
            
            # Iterate through shell windows
            for window in shell.Windows():
                try:
                    if window.HWND == hwnd:
                        location_url = window.LocationURL
                        if location_url.startswith("file:///"):
                            # Convert file:/// URL to Windows path
                            path = location_url[8:]  # Remove "file:///"
                            path = path.replace("/", "\\")  # Convert forward slashes
                            path = urllib.parse.unquote(path)  # Decode URL encoding
                            
                            # Validate the path
                            if os.path.isdir(path):
                                return path
                            else:
                                logger.warning(f"Invalid folder path: {path}")
                                return None
                except Exception as e:
                    logger.debug(f"Error processing shell window: {e}")
                    continue
                    
        finally:
            try:
                pythoncom.CoUninitialize()
            except pythoncom.com_error:
                # COM already uninitialized
                pass
                
    except Exception as e:
        logger.error(f"Error getting explorer folder path for {hwnd}: {e}")
        
    return None


def enum_top_level_windows() -> Generator[int, None, None]:
    """
    Generator function yielding HWNDs of all visible, top-level windows.
    
    Yields:
        int: Window handle (HWND)
    """
    def enum_windows_callback(hwnd, windows):
        try:
            if (win32gui.IsWindowVisible(hwnd) and 
                win32gui.GetParent(hwnd) == 0 and
                win32gui.GetWindowText(hwnd)):  # Has a title
                windows.append(hwnd)
        except Exception as e:
            logger.debug(f"Error in enum_windows_callback for {hwnd}: {e}")
        return True
    
    windows = []
    try:
        win32gui.EnumWindows(enum_windows_callback, windows)
    except Exception as e:
        logger.error(f"Error enumerating windows: {e}")
        
    for hwnd in windows:
        yield hwnd


def get_window_process_name(hwnd: int) -> Optional[str]:
    """
    Get the process name for a window.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        str: Process name (e.g., "notepad.exe") or None if failed
    """
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        process = psutil.Process(pid)
        return process.name()
    except Exception as e:
        logger.warning(f"Failed to get process name for window {hwnd}: {e}")
        return None


def is_system_window(hwnd: int) -> bool:
    """
    Check if a window is a system window that should be ignored.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if it's a system window
    """
    try:
        class_name = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        
        # Common system window classes to ignore
        system_classes = {
            "Shell_TrayWnd",      # Taskbar
            "Shell_SecondaryTrayWnd",  # Secondary taskbar
            "NotifyIconOverflowWindow",  # System tray overflow
            "Windows.UI.Core.CoreWindow",  # UWP apps
            "ApplicationFrameWindow",  # UWP app frame
            "ImmersiveLauncher",  # Start menu
            "SearchUI",          # Windows search
            "Shell_CharmWindow", # Charms bar
            "MultitaskingViewFrame",  # Task view
            "Shell_AppWnd",      # App windows
        }
        
        return class_name in system_classes or not title
    except Exception as e:
        logger.debug(f"Error checking if system window {hwnd}: {e}")
        return True


def enum_explorer_windows_with_paths() -> list:
    """
    Enumerate all open explorer.exe windows and their canonical folder paths.
    Returns a list of dicts: { 'hwnd': hwnd, 'path': canonical_path }
    """
    explorer_windows = []
    try:
        import win32gui
        for hwnd in enum_top_level_windows():
            try:
                class_name = win32gui.GetClassName(hwnd)
                if class_name == "CabinetWClass":
                    path = get_explorer_folder_path(hwnd)
                    if path:
                        explorer_windows.append({'hwnd': hwnd, 'path': path})
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Error enumerating explorer windows: {e}")
    return explorer_windows 