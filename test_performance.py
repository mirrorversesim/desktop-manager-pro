#!/usr/bin/env python3
"""
Performance testing script for Desktop Manager
Run this to profile CPU usage and identify bottlenecks
"""

import sys
import time
import threading
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.profiler import start_profiling, stop_profiling, start_cpu_monitoring, get_cpu_stats
from src.utils.cache import cache
from src.core.event_monitor import EventMonitor
from src.rules.engine import RuleEngine
from src.rules.config import ConfigManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_basic_performance():
    """Test basic performance without UI"""
    print("=== Desktop Manager Performance Test ===")
    
    # Start CPU monitoring
    start_cpu_monitoring(interval=1.0)
    
    # Load configuration
    config_manager = ConfigManager()
    rules = config_manager.load_rules()
    
    print(f"Loaded {len(rules)} rules")
    
    # Initialize rule engine
    rule_engine = RuleEngine(rules)
    
    # Create a dummy event callback
    def dummy_event_callback(event_id, hwnd, window_info):
        pass
    
    # Initialize event monitor
    event_monitor = EventMonitor(dummy_event_callback)
    
    print("Starting event monitoring...")
    event_monitor.start()
    
    # Monitor for 30 seconds
    print("Monitoring for 30 seconds...")
    start_time = time.time()
    
    while time.time() - start_time < 30:
        cpu_stats = get_cpu_stats()
        cache_stats = cache.get_stats()
        
        print(f"CPU: {cpu_stats['current']:.1f}% (avg: {cpu_stats['average']:.1f}%, max: {cpu_stats['max']:.1f}%)")
        print(f"Cache: {cache_stats['total_cache_size']} entries")
        
        time.sleep(5)
    
    # Stop monitoring
    event_monitor.stop()
    
    # Final stats
    final_cpu_stats = get_cpu_stats()
    final_cache_stats = cache.get_stats()
    
    print("\n=== Final Performance Results ===")
    print(f"CPU Usage - Current: {final_cpu_stats['current']:.1f}%")
    print(f"CPU Usage - Average: {final_cpu_stats['average']:.1f}%")
    print(f"CPU Usage - Maximum: {final_cpu_stats['max']:.1f}%")
    print(f"Cache Entries: {final_cache_stats['total_cache_size']}")
    print(f"Cache Hit Rate: {cache_stats.get('hit_rate', 'N/A')}")


def test_profiling():
    """Test with profiling enabled"""
    print("\n=== Starting Profiling Test ===")
    
    # Start profiling
    start_profiling()
    
    # Run basic test
    test_basic_performance()
    
    # Stop profiling and save results
    profile_file = stop_profiling(save_to_file=True)
    print(f"\nProfile saved to: {profile_file}")


def test_ui_performance():
    """Test UI performance"""
    print("\n=== Testing UI Performance ===")
    
    try:
        from src.ui.main_window import MainWindow
        
        # Start CPU monitoring
        start_cpu_monitoring(interval=1.0)
        
        # Create and run UI for 30 seconds
        app = MainWindow()
        
        # Run in a separate thread
        def run_ui():
            app.run()
        
        ui_thread = threading.Thread(target=run_ui, daemon=True)
        ui_thread.start()
        
        # Monitor for 30 seconds
        print("UI running for 30 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            cpu_stats = get_cpu_stats()
            print(f"UI CPU: {cpu_stats['current']:.1f}% (avg: {cpu_stats['average']:.1f}%)")
            time.sleep(5)
        
        # Close UI
        app.root.quit()
        
    except Exception as e:
        print(f"Error testing UI performance: {e}")


def main():
    """Main test function"""
    print("Desktop Manager Performance Testing")
    print("1. Basic performance test")
    print("2. Profiling test")
    print("3. UI performance test")
    print("4. All tests")
    
    choice = input("Choose test (1-4): ").strip()
    
    if choice == "1":
        test_basic_performance()
    elif choice == "2":
        test_profiling()
    elif choice == "3":
        test_ui_performance()
    elif choice == "4":
        test_basic_performance()
        test_profiling()
        test_ui_performance()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main() 