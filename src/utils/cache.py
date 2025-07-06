"""
Caching utilities for Desktop Manager
Reduces CPU usage by caching expensive operations
"""

import time
import threading
from typing import Any, Optional, Dict, Callable
from collections import OrderedDict
from .logger import get_logger

logger = get_logger(__name__)


class LRUCache:
    """Least Recently Used cache with TTL support"""
    
    def __init__(self, max_size: int = 100, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                # Check if expired
                if time.time() - self.timestamps[key] > self.ttl:
                    self._remove(key)
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        with self.lock:
            # Remove if exists
            if key in self.cache:
                self._remove(key)
            
            # Add new entry
            self.cache[key] = value
            self.timestamps[key] = time.time()
            
            # Remove oldest if cache is full
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)
    
    def _remove(self, key: str) -> None:
        """Remove key from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, timestamp in self.timestamps.items():
                if current_time - timestamp > self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


class ExpensiveOperationCache:
    """Cache for expensive operations with automatic cleanup"""
    
    def __init__(self):
        # Cache for executable paths (PID -> exe_path)
        self.exe_path_cache = LRUCache(max_size=200, ttl=600.0)  # 10 minutes TTL
        
        # Cache for explorer folder paths (hwnd -> folder_path)
        self.folder_path_cache = LRUCache(max_size=100, ttl=300.0)  # 5 minutes TTL
        
        # Cache for window info (hwnd -> window_info)
        self.window_info_cache = LRUCache(max_size=500, ttl=60.0)  # 1 minute TTL
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get_executable_path(self, pid: int) -> Optional[str]:
        """Get cached executable path for PID"""
        return self.exe_path_cache.get(f"exe_{pid}")
    
    def set_executable_path(self, pid: int, exe_path: str) -> None:
        """Cache executable path for PID"""
        self.exe_path_cache.set(f"exe_{pid}", exe_path)
    
    def get_folder_path(self, hwnd: int) -> Optional[str]:
        """Get cached folder path for window handle"""
        return self.folder_path_cache.get(f"folder_{hwnd}")
    
    def set_folder_path(self, hwnd: int, folder_path: str) -> None:
        """Cache folder path for window handle"""
        self.folder_path_cache.set(f"folder_{hwnd}", folder_path)
    
    def get_window_info(self, hwnd: int) -> Optional[Dict[str, Any]]:
        """Get cached window info for window handle"""
        return self.window_info_cache.get(f"window_{hwnd}")
    
    def set_window_info(self, hwnd: int, window_info: Dict[str, Any]) -> None:
        """Cache window info for window handle"""
        self.window_info_cache.set(f"window_{hwnd}", window_info)
    
    def _cleanup_loop(self):
        """Periodic cleanup of expired cache entries"""
        while True:
            try:
                time.sleep(60)  # Clean up every minute
                
                # Clean up all caches
                self.exe_path_cache.cleanup_expired()
                self.folder_path_cache.cleanup_expired()
                self.window_info_cache.cleanup_expired()
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                time.sleep(60)  # Wait before retrying
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "exe_path_cache_size": self.exe_path_cache.size(),
            "folder_path_cache_size": self.folder_path_cache.size(),
            "window_info_cache_size": self.window_info_cache.size(),
            "total_cache_size": (self.exe_path_cache.size() + 
                               self.folder_path_cache.size() + 
                               self.window_info_cache.size())
        }


# Global cache instance
cache = ExpensiveOperationCache()


def cached_executable_path(func: Callable) -> Callable:
    """Decorator to cache executable path lookups"""
    def wrapper(pid: int, *args, **kwargs):
        # Check cache first
        cached_result = cache.get_executable_path(pid)
        if cached_result is not None:
            return cached_result
        
        # Call original function
        result = func(pid, *args, **kwargs)
        
        # Cache result if successful
        if result:
            cache.set_executable_path(pid, result)
        
        return result
    
    return wrapper


def cached_folder_path(func: Callable) -> Callable:
    """Decorator to cache folder path lookups"""
    def wrapper(hwnd: int, *args, **kwargs):
        # Check cache first
        cached_result = cache.get_folder_path(hwnd)
        if cached_result is not None:
            return cached_result
        
        # Call original function
        result = func(hwnd, *args, **kwargs)
        
        # Cache result if successful
        if result:
            cache.set_folder_path(hwnd, result)
        
        return result
    
    return wrapper


def cached_window_info(func: Callable) -> Callable:
    """Decorator to cache window info lookups"""
    def wrapper(hwnd: int, *args, **kwargs):
        # Check cache first
        cached_result = cache.get_window_info(hwnd)
        if cached_result is not None:
            return cached_result
        
        # Call original function
        result = func(hwnd, *args, **kwargs)
        
        # Cache result if successful
        if result:
            cache.set_window_info(hwnd, result)
        
        return result
    
    return wrapper 