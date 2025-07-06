#!/usr/bin/env python3
"""
Desktop Manager Pro - Commercial Version
Main application entry point with modern UI
"""

import sys
import os
import threading
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.main_window import MainWindow
from src.utils.logger import get_logger


def main():
    """Main application entry point"""
    # Initialize logging
    logger = get_logger()
    logger.info("Desktop Manager Pro starting...")
    
    try:
        # Create and run the main application
        app = MainWindow()
        logger.info("Desktop Manager Pro started successfully")
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start Desktop Manager Pro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 