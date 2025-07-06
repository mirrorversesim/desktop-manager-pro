#!/usr/bin/env python3
"""
Test script to check logs functionality
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger

def test_logs():
    """Test logging functionality"""
    print("Testing Desktop Manager Logs...")
    
    # Get logger
    logger = get_logger("test_logs")
    
    # Test different log levels
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")
    
    # Check if log file exists
    log_file = Path("logs/desktop_manager.log")
    if log_file.exists():
        print(f"✅ Log file exists: {log_file}")
        print(f"   Size: {log_file.stat().st_size} bytes")
        
        # Read last few lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"   Total lines: {len(lines)}")
            print("   Last 5 lines:")
            for line in lines[-5:]:
                print(f"     {line.strip()}")
    else:
        print("❌ Log file not found")
    
    # Check logs directory
    logs_dir = Path("logs")
    if logs_dir.exists():
        print(f"✅ Logs directory exists: {logs_dir}")
        for file in logs_dir.iterdir():
            print(f"   Found: {file.name}")
    else:
        print("❌ Logs directory not found")

if __name__ == "__main__":
    test_logs() 