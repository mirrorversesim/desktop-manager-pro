#!/usr/bin/env python3
"""
Accurate Desktop Manager performance monitor
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

def monitor_with_activity(duration=60):
    """Monitor with activity detection"""
    proc = find_desktop_manager_process()
    
    if not proc:
        print("❌ Desktop Manager not found running")
        return
    
    print(f"✅ Found Desktop Manager (PID: {proc.pid})")
    print(f"Monitoring for {duration} seconds with high-frequency sampling...")
    print("-" * 70)
    
    cpu_samples = []
    memory_samples = []
    activity_detected = False
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            try:
                # Sample more frequently to catch spikes
                for _ in range(10):  # Sample 10 times per second
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    
                    cpu_samples.append(cpu_percent)
                    memory_samples.append(memory_mb)
                    
                    # Check for activity
                    if cpu_percent > 0.1:  # Any CPU usage above 0.1%
                        activity_detected = True
                        print(f"🔥 Activity detected! CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.1f} MB")
                    
                    time.sleep(0.1)
                
                # Print summary every second
                recent_cpu = cpu_samples[-10:]  # Last 10 samples
                avg_recent = sum(recent_cpu) / len(recent_cpu)
                max_recent = max(recent_cpu)
                current_memory = memory_samples[-1]
                
                print(f"Recent: Avg {avg_recent:.1f}% | Max {max_recent:.1f}% | Memory {current_memory:.1f} MB")
                print("-" * 70)
                
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
        
        # Count non-zero samples
        non_zero_samples = [x for x in cpu_samples if x > 0.1]
        activity_percentage = (len(non_zero_samples) / len(cpu_samples)) * 100
        
        avg_memory = sum(memory_samples) / len(memory_samples)
        max_memory = max(memory_samples)
        min_memory = min(memory_samples)
        
        print(f"\n📊 Detailed Performance Results:")
        print(f"CPU Usage:")
        print(f"  Average: {avg_cpu:.2f}%")
        print(f"  Maximum: {max_cpu:.2f}%")
        print(f"  Minimum: {min_cpu:.2f}%")
        print(f"  Activity detected: {activity_detected}")
        print(f"  Non-zero samples: {len(non_zero_samples)}/{len(cpu_samples)} ({activity_percentage:.1f}%)")
        
        if non_zero_samples:
            print(f"  Average when active: {sum(non_zero_samples)/len(non_zero_samples):.2f}%")
        
        print(f"Memory Usage:")
        print(f"  Average: {avg_memory:.1f} MB")
        print(f"  Maximum: {max_memory:.1f} MB")
        print(f"  Minimum: {min_memory:.1f} MB")
        print(f"Sample count: {len(cpu_samples)}")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if avg_cpu < 0.5:
            print("✅ CPU usage is excellent - very efficient")
        elif avg_cpu < 2:
            print("✅ CPU usage is good - running well")
        elif avg_cpu < 5:
            print("⚠️  CPU usage is moderate - acceptable")
        else:
            print("❌ CPU usage is high - may need optimization")
            
        if not activity_detected:
            print("🤔 No CPU activity detected - process might be idle or monitoring issue")
        else:
            print("✅ Process is actively working")

if __name__ == "__main__":
    monitor_with_activity() 