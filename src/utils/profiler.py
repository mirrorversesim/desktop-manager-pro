"""
Profiling utilities for Desktop Manager
Helps identify CPU bottlenecks and performance issues
"""

import cProfile
import pstats
import io
import time
import threading
from typing import Optional, Callable
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)


class PerformanceProfiler:
    """Performance profiler for identifying bottlenecks"""
    
    def __init__(self, output_dir: str = "logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.profiler = cProfile.Profile()
        self.is_profiling = False
        self.profile_data = None
    
    def start_profiling(self):
        """Start profiling"""
        if self.is_profiling:
            logger.warning("Profiling already in progress")
            return
        
        self.profiler.enable()
        self.is_profiling = True
        logger.info("Performance profiling started")
    
    def stop_profiling(self, save_to_file: bool = True) -> Optional[str]:
        """Stop profiling and optionally save results"""
        if not self.is_profiling:
            logger.warning("No profiling in progress")
            return None
        
        self.profiler.disable()
        self.is_profiling = False
        
        # Get stats
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        profile_output = s.getvalue()
        
        if save_to_file:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            profile_file = self.output_dir / f"profile_{timestamp}.txt"
            with open(profile_file, 'w') as f:
                f.write(profile_output)
            logger.info(f"Profile saved to {profile_file}")
            return str(profile_file)
        
        return profile_output
    
    def profile_function(self, func: Callable, *args, **kwargs):
        """Profile a single function call"""
        self.start_profiling()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.stop_profiling()


class CPUMonitor:
    """Monitor CPU usage patterns"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitoring = False
        self.thread = None
        self.cpu_samples = []
        self.max_samples = 1000
        self.logger = logger
    
    def start_monitoring(self):
        """Start CPU monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("CPU monitoring started")
    
    def stop_monitoring(self):
        """Stop CPU monitoring"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.info("CPU monitoring stopped")
    
    def _monitor_loop(self):
        """CPU monitoring loop"""
        import psutil
        
        # Get the current process
        current_process = psutil.Process()
        
        while self.monitoring:
            try:
                # Monitor the current process CPU usage, not system-wide
                cpu_percent = current_process.cpu_percent(interval=self.interval)
                timestamp = time.time()
                
                self.cpu_samples.append((timestamp, cpu_percent))
                
                # Keep only recent samples
                if len(self.cpu_samples) > self.max_samples:
                    self.cpu_samples = self.cpu_samples[-self.max_samples:]
                
                # Log high CPU usage (only for this process)
                if cpu_percent > 5.0:  # Log when CPU > 5%
                    self.logger.warning(f"High Desktop Manager CPU usage detected: {cpu_percent:.1f}%")
                    
            except Exception as e:
                self.logger.error(f"Error in CPU monitoring: {e}")
                time.sleep(self.interval)
    
    def get_cpu_stats(self) -> dict:
        """Get CPU usage statistics"""
        if not self.cpu_samples:
            return {"current": 0.0, "average": 0.0, "max": 0.0, "min": 0.0}
        
        current = self.cpu_samples[-1][1] if self.cpu_samples else 0.0
        values = [sample[1] for sample in self.cpu_samples]
        
        return {
            "current": current,
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "samples": len(values)
        }
    
    def get_recent_samples(self, count: int = 50) -> list:
        """Get recent CPU samples"""
        return self.cpu_samples[-count:] if self.cpu_samples else []


# Global profiler instance
profiler = PerformanceProfiler()
cpu_monitor = CPUMonitor()


def profile_function(func: Callable, *args, **kwargs):
    """Convenience function to profile a single function"""
    return profiler.profile_function(func, *args, **kwargs)


def start_profiling():
    """Start global profiling"""
    profiler.start_profiling()


def stop_profiling(save_to_file: bool = True) -> Optional[str]:
    """Stop global profiling"""
    return profiler.stop_profiling(save_to_file)


def start_cpu_monitoring(interval: float = 1.0):
    """Start CPU monitoring"""
    cpu_monitor.interval = interval
    cpu_monitor.start_monitoring()


def stop_cpu_monitoring():
    """Stop CPU monitoring"""
    cpu_monitor.stop_monitoring()


def get_cpu_stats() -> dict:
    """Get current CPU statistics"""
    return cpu_monitor.get_cpu_stats() 