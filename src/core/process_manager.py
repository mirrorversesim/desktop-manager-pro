import psutil
import win32api
import win32con
import win32process
from typing import Optional, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProcessManager:
    """Manager class for process operations"""
    
    def __init__(self):
        self.logger = logger
    
    def get_process_name(self, pid: int) -> Optional[str]:
        """Get the process name using psutil for robustness."""
        return get_process_name(pid)
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process exists and is running."""
        return is_process_running(pid)
    
    def terminate_process(self, pid: int, force: bool = False) -> bool:
        """Terminate a process gracefully or forcefully."""
        return terminate_process(pid, force)
    
    def get_process_children(self, pid: int) -> List[int]:
        """Get all child process IDs for a given process."""
        return get_process_children(pid)
    
    def get_process_info(self, pid: int) -> Optional[dict]:
        """Get comprehensive information about a process."""
        return get_process_info(pid)
    
    def find_processes_by_name(self, process_name: str) -> List[int]:
        """Find all running processes with a specific name."""
        return find_processes_by_name(process_name)
    
    def is_process_elevated(self, pid: int) -> bool:
        """Check if a process is running with elevated privileges."""
        return is_process_elevated(pid)


def get_process_name(pid: int) -> Optional[str]:
    """
    Get the process name using psutil for robustness.
    
    Args:
        pid (int): Process ID
        
    Returns:
        str: Process name (e.g., "notepad.exe") or None if failed
    """
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning(f"Failed to get process name for PID {pid}: {e}")
        return None


def is_process_running(pid: int) -> bool:
    """
    Check if a process exists and is running.
    
    Args:
        pid (int): Process ID
        
    Returns:
        bool: True if process is running
    """
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def terminate_process(pid: int, force: bool = False) -> bool:
    """
    Terminate a process gracefully or forcefully.
    
    Args:
        pid (int): Process ID
        force (bool): If True, force kill the process
        
    Returns:
        bool: True if process was terminated successfully
    """
    try:
        process = psutil.Process(pid)
        
        if force:
            # Force kill
            process.kill()
            logger.info(f"Force killed process {pid} ({process.name()})")
        else:
            # Graceful termination
            process.terminate()
            logger.info(f"Terminated process {pid} ({process.name()})")
            
        return True
        
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning(f"Failed to terminate process {pid}: {e}")
        return False


def get_process_children(pid: int) -> List[int]:
    """
    Get all child process IDs for a given process.
    
    Args:
        pid (int): Parent process ID
        
    Returns:
        List[int]: List of child process IDs
    """
    try:
        process = psutil.Process(pid)
        children = process.children(recursive=True)
        return [child.pid for child in children]
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning(f"Failed to get children for process {pid}: {e}")
        return []


def get_process_info(pid: int) -> Optional[dict]:
    """
    Get comprehensive information about a process.
    
    Args:
        pid (int): Process ID
        
    Returns:
        dict: Process information or None if failed
    """
    try:
        process = psutil.Process(pid)
        return {
            'pid': pid,
            'name': process.name(),
            'exe': process.exe(),
            'cmdline': process.cmdline(),
            'status': process.status(),
            'create_time': process.create_time(),
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'username': process.username()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning(f"Failed to get process info for PID {pid}: {e}")
        return None


def find_processes_by_name(process_name: str) -> List[int]:
    """
    Find all running processes with a specific name.
    
    Args:
        process_name (str): Process name to search for (e.g., "notepad.exe")
        
    Returns:
        List[int]: List of process IDs
    """
    pids = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.error(f"Error searching for processes by name {process_name}: {e}")
        
    return pids


def is_process_elevated(pid: int) -> bool:
    """
    Check if a process is running with elevated privileges.
    
    Args:
        pid (int): Process ID
        
    Returns:
        bool: True if process is elevated
    """
    try:
        process = psutil.Process(pid)
        return process.uids().real == 0  # On Windows, this checks for admin privileges
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning(f"Failed to check elevation for process {pid}: {e}")
        return False 