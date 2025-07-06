#!/usr/bin/env python3
"""
Quick performance check for Desktop Manager
"""

import psutil
import time
import os

def find_desktop_manager_processes():
    """Find all desktop manager processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'desktop_manager' in cmdline or 'run_pro.py' in cmdline or 'run_background.pyw' in cmdline:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def monitor_process_cpu(process, duration=30):
    """Monitor CPU usage of a specific process"""
    print(f"Monitoring process {process.pid} ({process.name()}) for {duration} seconds...")
    
    cpu_samples = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        try:
            cpu_percent = process.cpu_percent(interval=1.0)
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_samples.append(cpu_percent)
            
            print(f"CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.1f} MB")
            
        except psutil.NoSuchProcess:
            print("Process no longer running")
            break
        except Exception as e:
            print(f"Error monitoring process: {e}")
            break
    
    if cpu_samples:
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        min_cpu = min(cpu_samples)
        
        print(f"\n=== Results for PID {process.pid} ===")
        print(f"Average CPU: {avg_cpu:.1f}%")
        print(f"Maximum CPU: {max_cpu:.1f}%")
        print(f"Minimum CPU: {min_cpu:.1f}%")
        print(f"Sample count: {len(cpu_samples)}")

def main():
    """Main function"""
    print("Desktop Manager Performance Check")
    print("=" * 40)
    
    # Find desktop manager processes
    processes = find_desktop_manager_processes()
    
    if not processes:
        print("No desktop manager processes found running.")
        print("Make sure to start the desktop manager first (run_pro.py or run_background.pyw)")
        return
    
    print(f"Found {len(processes)} desktop manager process(es):")
    for i, proc in enumerate(processes):
        print(f"{i+1}. PID {proc.pid} - {proc.name()}")
    
    if len(processes) == 1:
        # Monitor the single process
        monitor_process_cpu(processes[0])
    else:
        # Let user choose
        choice = input(f"Choose process to monitor (1-{len(processes)}): ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(processes):
                monitor_process_cpu(processes[choice_idx])
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")

if __name__ == "__main__":
    main() 