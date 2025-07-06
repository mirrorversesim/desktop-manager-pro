#!/usr/bin/env python3
"""
Desktop Window & Process Manager - Background Version
Runs without console window and includes CPU monitoring.
"""

import sys
import time
import signal
import threading
import tkinter as tk
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger, get_logger
from src.rules.config import get_default_rules
from src.rules.engine import RuleEngine
from src.core.event_monitor import EventMonitor
from src.ui.tray import SystemTray


class BackgroundDesktopManager:
    """
    Background version of the desktop manager with system tray.
    """
    
    def __init__(self):
        """Initialize the background desktop manager."""
        self.logger = setup_logger("desktop_manager", log_level="INFO")
        self.event_monitor = None
        self.rule_engine = None
        self.system_tray = None
        self.running = False
        self.shutdown_event = threading.Event()
        
        self.logger.info("Background Desktop Manager initializing...")
        
    def initialize(self) -> bool:
        """
        Initialize all components of the application.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Load rules configuration
            self.logger.info("Loading rules configuration...")
            rules_config = get_default_rules()
            
            if not rules_config:
                self.logger.error("No rules loaded. Check the configuration file.")
                return False
                
            self.logger.info(f"Loaded {len(rules_config)} rules")
            
            # Create rule engine
            self.logger.info("Initializing rule engine...")
            self.rule_engine = RuleEngine(rules_config)
            
            # Create event monitor
            self.logger.info("Initializing event monitor...")
            self.event_monitor = EventMonitor(self.rule_engine.process_event)
            
            # Create system tray
            self.logger.info("Initializing system tray...")
            self.system_tray = SystemTray(self)
            
            self.logger.info("Initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the application.
        
        Returns:
            bool: True if started successfully
        """
        try:
            if not self.event_monitor or not self.rule_engine:
                self.logger.error("Components not initialized. Call initialize() first.")
                return False
            
            # Start the event monitor
            self.logger.info("Starting event monitor...")
            if not self.event_monitor.start():
                self.logger.error("Failed to start event monitor")
                return False
            
            # Start the system tray
            self.logger.info("Starting system tray...")
            self.system_tray.start()
            
            self.running = True
            self.logger.info("Background Desktop Manager started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        try:
            self.logger.info("Stopping Background Desktop Manager...")
            self.running = False
            
            # Stop the system tray
            if self.system_tray:
                self.system_tray.stop()
            
            # Stop the event monitor
            if self.event_monitor:
                self.event_monitor.stop()
            
            # Print final statistics
            if self.rule_engine:
                stats = self.rule_engine.get_statistics()
                self.logger.info("Final Statistics:")
                self.logger.info(f"  Total events processed: {stats['total_events_processed']}")
                self.logger.info(f"  Current windows tracked: {stats['current_windows_tracked']}")
                self.logger.info(f"  Enabled rules: {stats['enabled_rules']}")
                self.logger.info("  Rule execution counts:")
                for rule_name, count in stats['rule_execution_counts'].items():
                    self.logger.info(f"    {rule_name}: {count}")
            
            self.logger.info("Background Desktop Manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def run(self) -> None:
        """
        Run the main application loop.
        """
        try:
            # Initialize the application
            if not self.initialize():
                self.logger.error("Failed to initialize application")
                return
            
            # Start the application
            if not self.start():
                self.logger.error("Failed to start application")
                return
            
            # Show system tray event log
            if self.system_tray:
                self.system_tray.show_event_log()
            
            # Main loop - keep the application running
            try:
                while self.running and not self.shutdown_event.is_set():
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal")
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger = get_logger("main")
    logger.info(f"Received signal {signum}")
    if hasattr(signal_handler, 'app'):
        signal_handler.app.shutdown_event.set()


def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the application
    app = BackgroundDesktopManager()
    signal_handler.app = app  # Store reference for signal handler
    
    try:
        app.run()
    except Exception as e:
        logger = get_logger("main")
        logger.error(f"Unhandled exception in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 