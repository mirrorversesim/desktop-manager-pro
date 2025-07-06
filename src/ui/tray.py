import threading
import time
import psutil
import tkinter as tk
from tkinter import scrolledtext, messagebox
import win32gui
import win32con
import win32api
from PIL import Image, ImageTk
import io
import os
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pystray
    from pystray import MenuItem as item
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logger.warning("pystray not available - system tray functionality will be limited")


class SystemTray:
    """
    System tray interface with proper icon and menu functionality.
    """
    
    def __init__(self, desktop_manager):
        """
        Initialize the system tray.
        
        Args:
            desktop_manager: Reference to the main desktop manager
        """
        self.desktop_manager = desktop_manager
        self.tray_icon = None
        self.monitoring_thread = None
        self.running = False
        self.cpu_usage = 0.0
        self.event_log_window = None
        self.is_hidden = False
        
        # Create tray icon
        self.create_tray_icon()
        
    def create_tray_icon(self):
        """Create the system tray icon."""
        if not PYSTRAY_AVAILABLE:
            logger.warning("pystray not available - cannot create system tray icon")
            return
            
        try:
            # Try to use the existing icon file
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.icon_image = Image.open(icon_path)
            else:
                # Create a simple default icon
                self.icon_image = self.create_default_icon()
            
            # Create the tray menu
            menu = pystray.Menu(
                item('Show Window', self.show_window),
                item('Event Log', self.show_event_log),
                pystray.Menu.SEPARATOR,
                item('Quit', self.quit_app)
            )
            
            # Create the tray icon
            self.tray_icon = pystray.Icon(
                "desktop_manager",
                self.icon_image,
                "Desktop Manager Pro",
                menu
            )
            
            logger.info("System tray icon created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tray icon: {e}")
            self.tray_icon = None
    
    def create_default_icon(self):
        """Create a simple default icon."""
        # Create a 16x16 blue square icon
        img = Image.new('RGBA', (16, 16), (0, 127, 255, 255))
        return img
    
    def start(self):
        """Start the system tray icon."""
        if not self.tray_icon:
            logger.warning("No tray icon available")
            return
            
        try:
            # Start the tray icon in a separate thread
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
            
            # Start monitoring thread
            self.running = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("System tray started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start system tray: {e}")
    
    def stop(self):
        """Stop the system tray icon."""
        self.running = False
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception as e:
                logger.error(f"Error stopping tray icon: {e}")
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            
        logger.info("System tray stopped")
    
    def hide_window(self):
        """Hide the main window to system tray."""
        if not self.tray_icon:
            logger.warning("No tray icon available - cannot hide window")
            return False
            
        try:
            self.desktop_manager.root.withdraw()
            self.is_hidden = True
            
            # Update tray icon tooltip
            if hasattr(self.tray_icon, 'title'):
                self.tray_icon.title = "Desktop Manager Pro (Hidden) - Click to show"
            
            logger.info("Window hidden to system tray")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hide window: {e}")
            return False
    
    def show_window(self, icon=None, item=None):
        """Show the main window from system tray."""
        try:
            self.desktop_manager.root.deiconify()
            self.desktop_manager.root.lift()
            self.desktop_manager.root.focus_force()
            self.is_hidden = False
            
            # Update tray icon tooltip
            if hasattr(self.tray_icon, 'title'):
                self.tray_icon.title = "Desktop Manager Pro"
            
            logger.info("Window restored from system tray")
            
        except Exception as e:
            logger.error(f"Failed to show window: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        try:
            if messagebox.askyesno("Quit", "Are you sure you want to quit Desktop Manager?"):
                self.stop()
                if self.desktop_manager:
                    self.desktop_manager.quit_app()
        except Exception as e:
            logger.error(f"Error in quit_app: {e}")
    
    def _monitor_loop(self):
        """Monitor CPU usage and update tray icon."""
        while self.running:
            try:
                # Get CPU usage
                self.cpu_usage = psutil.cpu_percent(interval=1)
                
                # Update tray icon tooltip with status
                if self.tray_icon and hasattr(self.tray_icon, 'title'):
                    stats = self.desktop_manager.rule_engine.get_statistics() if self.desktop_manager.rule_engine else {}
                    status = "Hidden" if self.is_hidden else "Active"
                    tooltip = f"Desktop Manager Pro ({status})\nCPU: {self.cpu_usage:.1f}%\nEvents: {stats.get('total_events_processed', 0)}"
                    self.tray_icon.title = tooltip
                    
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in tray monitoring: {e}")
                time.sleep(10)
    
    def show_event_log(self, icon=None, item=None):
        """Show a simple event log window."""
        if self.event_log_window:
            try:
                self.event_log_window.deiconify()
                self.event_log_window.lift()
                self.event_log_window.focus_force()
                return
            except tk.TclError:
                # Window was destroyed, create new one
                pass
            
        # Create event log window
        self.event_log_window = tk.Toplevel()
        self.event_log_window.title("Desktop Manager - Event Log")
        self.event_log_window.geometry("600x400")
        self.event_log_window.resizable(True, True)
        
        # CPU usage display
        cpu_frame = tk.Frame(self.event_log_window)
        cpu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cpu_label = tk.Label(cpu_frame, text="CPU Usage: 0.0%")
        self.cpu_label.pack(side=tk.LEFT)
        
        # Statistics display
        stats_frame = tk.Frame(self.event_log_window)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Events: 0 | Windows: 0 | Rules: 0")
        self.stats_label.pack(side=tk.LEFT)
        
        # Event log
        log_frame = tk.Frame(self.event_log_window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(self.event_log_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Refresh", command=self._refresh_log).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.event_log_window.withdraw).pack(side=tk.RIGHT, padx=5)
        
        # Update log periodically
        self._update_log()
        
        # Handle window close
        self.event_log_window.protocol("WM_DELETE_WINDOW", self.event_log_window.withdraw)
    
    def _update_log(self):
        """Update the event log display."""
        if not self.event_log_window or not self.running:
            return
            
        try:
            # Update CPU usage
            self.cpu_label.config(text=f"CPU Usage: {self.cpu_usage:.1f}%")
            
            # Update statistics
            if self.desktop_manager.rule_engine:
                stats = self.desktop_manager.rule_engine.get_statistics()
                self.stats_label.config(
                    text=f"Events: {stats.get('total_events_processed', 0)} | "
                         f"Windows: {stats.get('current_windows_tracked', 0)} | "
                         f"Rules: {stats.get('enabled_rules', 0)}"
                )
            
            # Add recent log entries (this would need to be implemented with a custom log handler)
            # For now, just show a simple status
            current_time = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{current_time}] System running - CPU: {self.cpu_usage:.1f}%\n")
            self.log_text.see(tk.END)
            
            # Keep only last 100 lines
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 100:
                self.log_text.delete("1.0", f"{len(lines)-100}.0")
            
        except Exception as e:
            logger.error(f"Error updating log: {e}")
        
        # Schedule next update
        if self.event_log_window:
            self.event_log_window.after(2000, self._update_log)
    
    def _refresh_log(self):
        """Refresh the log display."""
        self._update_log()
    
    def _clear_log(self):
        """Clear the log display."""
        self.log_text.delete("1.0", tk.END)
    
    def get_status(self):
        """Get current status information."""
        return {
            'cpu_usage': self.cpu_usage,
            'running': self.running,
            'is_hidden': self.is_hidden,
            'tray_available': self.tray_icon is not None,
            'desktop_manager_running': self.desktop_manager.running if self.desktop_manager else False
        } 