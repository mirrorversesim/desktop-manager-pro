#!/usr/bin/env python3
"""
Simple CPU usage monitor
"""

import psutil
import time

def monitor_system_cpu(duration=30):
    """Monitor overall system CPU usage"""
    print(f"Monitoring system CPU usage for {duration} seconds...")
    print("Press Ctrl+C to stop early")
    print("-" * 50)
    
    cpu_samples = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            cpu_percent = psutil.cpu_percent(interval=1.0)
            memory_percent = psutil.virtual_memory().percent
            cpu_samples.append(cpu_percent)
            
            print(f"System CPU: {cpu_percent:.1f}% | Memory: {memory_percent:.1f}%")
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    if cpu_samples:
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        min_cpu = min(cpu_samples)
        
        print(f"\n=== System CPU Results ===")
        print(f"Average CPU: {avg_cpu:.1f}%")
        print(f"Maximum CPU: {max_cpu:.1f}%")
        print(f"Minimum CPU: {min_cpu:.1f}%")
        print(f"Sample count: {len(cpu_samples)}")
        
        # Give a simple assessment
        if avg_cpu < 5:
            print("✅ CPU usage is very low - system running efficiently")
        elif avg_cpu < 15:
            print("✅ CPU usage is low - system running well")
        elif avg_cpu < 30:
            print("⚠️  CPU usage is moderate")
        else:
            print("❌ CPU usage is high - may indicate performance issues")

if __name__ == "__main__":
    monitor_system_cpu() 