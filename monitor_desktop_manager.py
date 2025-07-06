#!/usr/bin/env python3
"""
Monitor Desktop Manager specific performance
"""

import psutil
import time
import os

def find_desktop_manager_process():
    """Find the desktop manager process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'run_pro.py' in cmdline or 'run_background.pyw' in cmdline:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def monitor_desktop_manager(duration=60):
    """Monitor desktop manager performance"""
    proc = find_desktop_manager_process()
    
    if not proc:
        print("❌ Desktop Manager not found running")
        print("Start it with: python run_pro.py")
        return
    
    print(f"✅ Found Desktop Manager (PID: {proc.pid})")
    print(f"Monitoring for {duration} seconds...")
    print("-" * 60)
    
    cpu_samples = []
    memory_samples = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            try:
                # Get process stats
                cpu_percent = proc.cpu_percent(interval=1.0)
                memory_mb = proc.memory_info().rss / 1024 / 1024
                
                cpu_samples.append(cpu_percent)
                memory_samples.append(memory_mb)
                
                # Get system stats for comparison
                system_cpu = psutil.cpu_percent(interval=0.1)
                system_memory = psutil.virtual_memory().percent
                
                print(f"Desktop Manager: CPU {cpu_percent:5.1f}% | Memory {memory_mb:6.1f} MB")
                print(f"System Total:    CPU {system_cpu:5.1f}% | Memory {system_memory:5.1f}%")
                print("-" * 60)
                
            except psutil.NoSuchProcess:
                print("❌ Desktop Manager process ended")
                break
            except Exception as e:
                print(f"Error monitoring: {e}")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    
    if cpu_samples:
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        min_cpu = min(cpu_samples)
        
        avg_memory = sum(memory_samples) / len(memory_samples)
        max_memory = max(memory_samples)
        min_memory = min(memory_samples)
        
        print(f"\n📊 Desktop Manager Performance Results:")
        print(f"CPU Usage:")
        print(f"  Average: {avg_cpu:.1f}%")
        print(f"  Maximum: {max_cpu:.1f}%")
        print(f"  Minimum: {min_cpu:.1f}%")
        print(f"Memory Usage:")
        print(f"  Average: {avg_memory:.1f} MB")
        print(f"  Maximum: {max_memory:.1f} MB")
        print(f"  Minimum: {min_memory:.1f} MB")
        print(f"Sample count: {len(cpu_samples)}")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if avg_cpu < 2:
            print("✅ CPU usage is excellent - very efficient")
        elif avg_cpu < 5:
            print("✅ CPU usage is good - running well")
        elif avg_cpu < 10:
            print("⚠️  CPU usage is moderate - acceptable")
        else:
            print("❌ CPU usage is high - may need optimization")
            
        if avg_memory < 50:
            print("✅ Memory usage is excellent - very lightweight")
        elif avg_memory < 100:
            print("✅ Memory usage is good - reasonable")
        elif avg_memory < 200:
            print("⚠️  Memory usage is moderate - acceptable")
        else:
            print("❌ Memory usage is high - may need optimization")

if __name__ == "__main__":
    monitor_desktop_manager() 