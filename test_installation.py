#!/usr/bin/env python3
"""
Test script to verify Desktop Manager installation and dependencies.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test core modules
        from src.utils.logger import setup_logger, get_logger
        print("✓ Logger module imported successfully")
        
        from src.utils.win32_helpers import get_window_info, enum_top_level_windows
        print("✓ Win32 helpers module imported successfully")
        
        from src.core.window_manager import minimize_window, close_window
        print("✓ Window manager module imported successfully")
        
        from src.core.process_manager import get_process_name, is_process_running
        print("✓ Process manager module imported successfully")
        
        from src.core.event_monitor import EventMonitor
        print("✓ Event monitor module imported successfully")
        
        from src.rules.config import load_rules, get_default_rules
        print("✓ Rules config module imported successfully")
        
        from src.rules.actions import perform_action, get_supported_actions
        print("✓ Rules actions module imported successfully")
        
        from src.rules.engine import RuleEngine
        print("✓ Rules engine module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_windows_api():
    """Test basic Windows API functionality."""
    print("\nTesting Windows API...")
    
    try:
        import win32gui
        import win32con
        import psutil
        
        # Test basic Windows API calls
        desktop_hwnd = win32gui.GetDesktopWindow()
        print(f"✓ Desktop window handle: {desktop_hwnd}")
        
        # Test process enumeration
        processes = list(psutil.process_iter(['pid', 'name']))[:5]
        print(f"✓ Found {len(processes)} processes (showing first 5)")
        
        return True
        
    except Exception as e:
        print(f"✗ Windows API error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from src.rules.config import get_default_rules
        
        rules = get_default_rules()
        print(f"✓ Loaded {len(rules)} rules from configuration")
        
        if rules:
            print("  Sample rule:")
            rule = rules[0]
            print(f"    Name: {rule.get('name', 'Unknown')}")
            print(f"    Enabled: {rule.get('enabled', False)}")
            print(f"    Event Type: {rule.get('trigger', {}).get('event_type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_logging():
    """Test logging functionality."""
    print("\nTesting logging...")
    
    try:
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test_logger", log_level="INFO")
        logger.info("Test log message")
        print("✓ Logging system working")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging error: {e}")
        return False

def main():
    """Run all tests."""
    print("Desktop Manager Installation Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Windows API", test_windows_api),
        ("Configuration", test_configuration),
        ("Logging", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name} test failed")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Installation is successful.")
        print("\nYou can now run the application with:")
        print("  python main.py")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run pywin32 post-install: python -m pywin32_postinstall -install")
        print("3. Run as Administrator if needed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 