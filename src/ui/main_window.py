"""
Main window UI for Desktop Manager
Modern, user-friendly interface with unique design elements
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from .tray import SystemTray
from ..core.event_monitor import EventMonitor
from ..core.process_manager import ProcessManager
from ..core.window_manager import WindowManager
from ..rules.engine import RuleEngine
from ..rules.config import ConfigManager
from ..utils.logger import get_logger
from ..utils.profiler import get_cpu_stats
from ..utils.autostart import is_autostart_enabled, toggle_autostart
from .welcome_dialog import show_welcome_dialog



class ModernButton(tk.Canvas):
    """Custom modern button with hover effects and gradients"""
    
    def __init__(self, parent, text, command=None, width=120, height=40, 
                 bg_color="#4A90E2", hover_color="#357ABD", text_color="white"):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget('bg'), highlightthickness=0)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw_button()
    
    def _draw_button(self, is_hover=False, is_pressed=False):
        self.delete("all")
        
        color = self.hover_color if is_hover else self.bg_color
        if is_pressed:
            color = self._darken_color(color, 0.2)
        
        # Draw rounded rectangle
        radius = 8
        self.create_rounded_rectangle(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                                    radius, fill=color, outline="")
        
        # Add gradient effect
        for i in range(5):
            alpha = 0.1 - (i * 0.02)
            self.create_rounded_rectangle(2, 2+i, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                                        radius, fill=self._lighten_color(color, alpha), outline="")
        
        # Add text
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.text, fill=self.text_color, font=("Segoe UI", 10, "bold"))
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _lighten_color(self, color, factor):
        """Lighten a color by a factor"""
        # Simple color lightening - in production you'd want a proper color library
        return color
    
    def _darken_color(self, color, factor):
        """Darken a color by a factor"""
        # Simple color darkening - in production you'd want a proper color library
        return color
    
    def _on_enter(self, event):
        self._draw_button(is_hover=True)
    
    def _on_leave(self, event):
        self._draw_button()
    
    def _on_click(self, event):
        self._draw_button(is_hover=True, is_pressed=True)
    
    def _on_release(self, event):
        self._draw_button(is_hover=True)
        if self.command:
            self.command()





class RuleCard(tk.Frame):
    """Card widget for displaying and editing rules"""
    
    def __init__(self, parent, rule_data, on_edit=None, on_delete=None):
        super().__init__(parent, bg="#FFFFFF", relief="flat", bd=1)
        
        self.rule_data = rule_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Create card content
        self._create_card()
    
    def _create_card(self):
        """Create the card layout"""
        # Header
        header_frame = tk.Frame(self, bg="#F8F9FA", height=40)
        header_frame.pack(fill="x", padx=1, pady=(1, 0))
        header_frame.pack_propagate(False)
        
        # Rule name
        name_label = tk.Label(header_frame, text=self.rule_data.get("name", "Unnamed Rule"), 
                             font=("Segoe UI", 11, "bold"), bg="#F8F9FA", fg="#2C3E50")
        name_label.pack(side="left", padx=10, pady=10)
        
        # Status indicator
        status_color = "#27AE60" if self.rule_data.get("enabled", True) else "#E74C3C"
        status_label = tk.Label(header_frame, text="●", font=("Segoe UI", 16), 
                               bg="#F8F9FA", fg=status_color)
        status_label.pack(side="right", padx=10, pady=10)
        
        # Content
        content_frame = tk.Frame(self, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Rule description
        desc_text = self.rule_data.get("description", "No description")
        desc_label = tk.Label(content_frame, text=desc_text, 
                             font=("Segoe UI", 9), bg="#FFFFFF", fg="#7F8C8D",
                             wraplength=250, justify="left")
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Rule details
        details_frame = tk.Frame(content_frame, bg="#FFFFFF")
        details_frame.pack(fill="x")
        
        # Trigger
        trigger_text = f"Trigger: {self.rule_data.get('trigger', {}).get('type', 'Unknown')}"
        trigger_label = tk.Label(details_frame, text=trigger_text, 
                                font=("Segoe UI", 8), bg="#FFFFFF", fg="#95A5A6")
        trigger_label.pack(anchor="w")
        
        # Action
        action_text = f"Action: {self.rule_data.get('action', {}).get('type', 'Unknown')}"
        action_label = tk.Label(details_frame, text=action_text, 
                               font=("Segoe UI", 8), bg="#FFFFFF", fg="#95A5A6")
        action_label.pack(anchor="w")
        
        # Buttons
        button_frame = tk.Frame(self, bg="#FFFFFF")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        if self.on_edit:
            edit_btn = tk.Button(button_frame, text="Edit", 
                                command=lambda: self.on_edit(self.rule_data),
                                font=("Segoe UI", 8), bg="#3498DB", fg="white",
                                relief="flat", padx=15, pady=2)
            edit_btn.pack(side="left", padx=(0, 5))
        
        if self.on_delete:
            delete_btn = tk.Button(button_frame, text="Delete", 
                                  command=lambda: self.on_delete(self.rule_data),
                                  font=("Segoe UI", 8), bg="#E74C3C", fg="white",
                                  relief="flat", padx=15, pady=2)
            delete_btn.pack(side="left")


class MainWindow:
    """Main application window with modern UI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Desktop Manager Pro")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configure window
        self.root.configure(bg="#ECF0F1")
        self.root.iconbitmap("assets/icon.ico") if Path("assets/icon.ico").exists() else None
        
        # Initialize components
        self.logger = get_logger()
        self.config_manager = ConfigManager()
        self.process_manager = ProcessManager()
        self.window_manager = WindowManager()
        
        # Load rules and initialize rule engine
        self.rules = self.config_manager.load_rules()
        self.rule_engine = RuleEngine(self.rules)
        self.event_monitor = EventMonitor(self.rule_engine.process_event)
        self.system_tray = SystemTray(self)
        
        # UI state
        self.rules = []
        self.stats = {
            "events_processed": 0,
            "rules_triggered": 0,
            "windows_managed": 0,
            "cpu_usage": 0.0
        }
        
        # Show welcome dialog first
        if not show_welcome_dialog(self.root):
            return  # User declined, app will close
        
        # Create UI
        self._create_ui()
        
        # Start monitoring
        self._start_monitoring()
        
        # Start CPU monitoring
        from ..utils.profiler import start_cpu_monitoring
        start_cpu_monitoring(interval=2.0)
        

        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Escape>", lambda e: self.hide_window())
    
    def _create_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#ECF0F1")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg="#ECF0F1")
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_rules_tab()
        self._create_settings_tab()
        self._create_logs_tab()
    
    def _create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg="#2C3E50", height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="Desktop Manager Pro", 
                              font=("Segoe UI", 24, "bold"), 
                              bg="#2C3E50", fg="white")
        title_label.pack(side="left", padx=20, pady=20)
        
        # Status indicator
        self.status_label = tk.Label(header_frame, text="● Active", 
                                    font=("Segoe UI", 12), 
                                    bg="#2C3E50", fg="#27AE60")
        self.status_label.pack(side="right", padx=20, pady=20)
        
        # Minimize to tray button
        minimize_btn = tk.Button(header_frame, text="Minimize to Tray", 
                                command=self.hide_window,
                                font=("Segoe UI", 10), bg="#34495E", fg="white",
                                relief="flat", padx=15, pady=5)
        minimize_btn.pack(side="right", padx=(0, 10), pady=20)
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab"""
        dashboard_frame = tk.Frame(self.notebook, bg="#ECF0F1")
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Stats cards
        stats_frame = tk.Frame(dashboard_frame, bg="#ECF0F1")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Create stat cards
        self._create_stat_card(stats_frame, "Events Processed", "0", "#3498DB", 0, 0)
        self._create_stat_card(stats_frame, "Rules Triggered", "0", "#27AE60", 0, 1)
        self._create_stat_card(stats_frame, "Windows Managed", "0", "#E67E22", 0, 2)
        self._create_stat_card(stats_frame, "CPU Usage", "0%", "#E74C3C", 0, 3)

        

        
        # Recent activity
        activity_frame = tk.LabelFrame(dashboard_frame, text="Recent Activity", 
                                      font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        activity_frame.pack(fill="both", expand=True)
        
        # Activity list
        self.activity_list = tk.Listbox(activity_frame, font=("Consolas", 9), 
                                       bg="#FFFFFF", fg="#2C3E50", 
                                       selectmode="none", relief="flat")
        self.activity_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add some sample activity
        self.activity_list.insert(0, "17:51:03 - Rule 'Manage Duplicate Folder Windows' triggered")
        self.activity_list.insert(0, "17:50:45 - New Notepad window detected")
        self.activity_list.insert(0, "17:50:30 - Application started successfully")
    
    def _create_stat_card(self, parent, title, value, color, row, col):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg="white", relief="flat", bd=1)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Value
        value_label = tk.Label(card_frame, text=value, font=("Segoe UI", 24, "bold"), 
                              bg="white", fg=color)
        value_label.pack(pady=(15, 5))
        
        # Title
        title_label = tk.Label(card_frame, text=title, font=("Segoe UI", 10), 
                              bg="white", fg="#7F8C8D")
        title_label.pack(pady=(0, 15))
        
        # Store reference for updates
        if title == "Events Processed":
            self.events_label = value_label
        elif title == "Rules Triggered":
            self.rules_label = value_label
        elif title == "Windows Managed":
            self.windows_label = value_label
        elif title == "CPU Usage":
            self.cpu_label = value_label
    
    def _create_rules_tab(self):
        """Create the rules management tab"""
        rules_frame = tk.Frame(self.notebook, bg="#ECF0F1")
        self.notebook.add(rules_frame, text="Rules")
        
        # Toolbar
        toolbar_frame = tk.Frame(rules_frame, bg="#ECF0F1")
        toolbar_frame.pack(fill="x", pady=(0, 20))
        
        add_btn = ModernButton(toolbar_frame, "Add Rule", self._add_rule, 
                              width=100, height=35, bg_color="#27AE60", hover_color="#229954")
        add_btn.pack(side="left")
        
        import_btn = ModernButton(toolbar_frame, "Import Rules", self._import_rules, 
                                 width=100, height=35, bg_color="#3498DB", hover_color="#2980B9")
        import_btn.pack(side="left", padx=(10, 0))
        
        export_btn = ModernButton(toolbar_frame, "Export Rules", self._export_rules, 
                                 width=100, height=35, bg_color="#E67E22", hover_color="#D35400")
        export_btn.pack(side="left", padx=(10, 0))
        
        # Rules container
        rules_container = tk.Frame(rules_frame, bg="#ECF0F1")
        rules_container.pack(fill="both", expand=True)
        
        # Create scrollable canvas for rules
        canvas = tk.Canvas(rules_container, bg="#ECF0F1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(rules_container, orient="vertical", command=canvas.yview)
        self.rules_scrollable_frame = tk.Frame(canvas, bg="#ECF0F1")
        
        self.rules_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.rules_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing rules
        self._load_rules()
    
    def _create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = tk.Frame(self.notebook, bg="#ECF0F1")
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings container
        settings_container = tk.Frame(settings_frame, bg="#ECF0F1")
        settings_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # General settings
        general_frame = tk.LabelFrame(settings_container, text="General Settings", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        general_frame.pack(fill="x", pady=(0, 20))
        
        # Auto-start
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        autostart_check = tk.Checkbutton(general_frame, text="Start with Windows", 
                                        variable=self.autostart_var, font=("Segoe UI", 10),
                                        bg="#ECF0F1", fg="#2C3E50")
        autostart_check.pack(anchor="w", padx=20, pady=10)
        
        # Minimize to tray
        minimize_var = tk.BooleanVar(value=True)
        minimize_check = tk.Checkbutton(general_frame, text="Minimize to system tray", 
                                       variable=minimize_var, font=("Segoe UI", 10),
                                       bg="#ECF0F1", fg="#2C3E50")
        minimize_check.pack(anchor="w", padx=20, pady=10)
        
        # Performance settings
        perf_frame = tk.LabelFrame(settings_container, text="Performance", 
                                  font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        perf_frame.pack(fill="x", pady=(0, 20))
        
        # Polling interval
        interval_frame = tk.Frame(perf_frame, bg="#ECF0F1")
        interval_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(interval_frame, text="Polling Interval (seconds):", 
                font=("Segoe UI", 10), bg="#ECF0F1", fg="#2C3E50").pack(side="left")
        
        self.interval_var = tk.StringVar(value="3.0")
        interval_entry = tk.Entry(interval_frame, textvariable=self.interval_var, 
                                 font=("Segoe UI", 10), width=10)
        interval_entry.pack(side="left", padx=(10, 0))
        
        # Apply button
        apply_btn = tk.Button(interval_frame, text="Apply", 
                             command=self._apply_polling_interval,
                             font=("Segoe UI", 9), bg="#3498DB", fg="white",
                             relief="flat", padx=10, pady=2)
        apply_btn.pack(side="left", padx=(10, 0))
        
        # Current status
        self.interval_status_label = tk.Label(interval_frame, text="Current: 3.0s", 
                                             font=("Segoe UI", 9), bg="#ECF0F1", fg="#7F8C8D")
        self.interval_status_label.pack(side="right")
        
        # Save button
        save_btn = ModernButton(settings_container, "Save Settings", self._save_settings, 
                               width=120, height=40, bg_color="#27AE60", hover_color="#229954")
        save_btn.pack(pady=20)
    
    def _create_logs_tab(self):
        """Create the logs tab"""
        logs_frame = tk.Frame(self.notebook, bg="#ECF0F1")
        self.notebook.add(logs_frame, text="Logs")
        
        # Log controls
        controls_frame = tk.Frame(logs_frame, bg="#ECF0F1")
        controls_frame.pack(fill="x", pady=(0, 20))
        
        refresh_btn = ModernButton(controls_frame, "Refresh", self._refresh_logs, 
                                  width=80, height=30, bg_color="#3498DB", hover_color="#2980B9")
        refresh_btn.pack(side="left")
        
        clear_btn = ModernButton(controls_frame, "Clear Logs", self._clear_logs, 
                                width=80, height=30, bg_color="#E74C3C", hover_color="#C0392B")
        clear_btn.pack(side="left", padx=(10, 0))
        
        # Log display
        log_frame = tk.Frame(logs_frame, bg="#ECF0F1")
        log_frame.pack(fill="both", expand=True)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(text_frame, font=("Consolas", 9), bg="#2C3E50", fg="#ECF0F1",
                               insertbackground="#ECF0F1", relief="flat", wrap="word")
        log_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Load initial logs
        self._refresh_logs()
    
    def _load_rules(self):
        """Load and display existing rules"""
        try:
            rules = self.config_manager.load_rules()
            self.rules = rules
            
            # Clear existing rules
            for widget in self.rules_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Create rule cards
            for rule in rules:
                card = RuleCard(self.rules_scrollable_frame, rule, 
                               on_edit=self._edit_rule, on_delete=self._delete_rule)
                card.pack(fill="x", pady=(0, 10))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rules: {e}")
    
    def _add_rule(self):
        """Add a new rule"""
        from .rule_editor import show_rule_editor
        
        def save_rule(rule_data):
            self.rules.append(rule_data)
            self.config_manager.save_rules(self.rules)
            self._load_rules()
        
        show_rule_editor(self.root, on_save=save_rule)
    
    def _edit_rule(self, rule):
        """Edit an existing rule"""
        from .rule_editor import show_rule_editor
        
        def save_rule(rule_data):
            # Replace the old rule with the new one
            for i, existing_rule in enumerate(self.rules):
                if existing_rule == rule:
                    self.rules[i] = rule_data
                    break
            self.config_manager.save_rules(self.rules)
            self._load_rules()
        
        show_rule_editor(self.root, rule_data=rule, on_save=save_rule)
    
    def _delete_rule(self, rule):
        """Delete a rule"""
        if messagebox.askyesno("Delete Rule", f"Are you sure you want to delete '{rule.get('name', 'Unknown')}'?"):
            # Remove from list and save
            self.rules = [r for r in self.rules if r != rule]
            self.config_manager.save_rules(self.rules)
            self._load_rules()
    
    def _import_rules(self):
        """Import rules from file"""
        filename = filedialog.askopenfilename(
            title="Import Rules",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    rules = json.load(f)
                self.rules.extend(rules)
                self.config_manager.save_rules(self.rules)
                self._load_rules()
                messagebox.showinfo("Success", f"Imported {len(rules)} rules")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import rules: {e}")
    
    def _export_rules(self):
        """Export rules to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Rules",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.rules, f, indent=2)
                messagebox.showinfo("Success", f"Exported {len(self.rules)} rules")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export rules: {e}")
    
    def _apply_polling_interval(self):
        """Apply the new polling interval"""
        try:
            new_interval = float(self.interval_var.get())
            if hasattr(self, 'event_monitor') and self.event_monitor:
                success = self.event_monitor.set_polling_interval(new_interval)
                if success:
                    self.interval_status_label.config(text=f"Current: {new_interval}s")
                    messagebox.showinfo("Success", f"Polling interval changed to {new_interval} seconds")
                else:
                    messagebox.showerror("Error", "Failed to change polling interval")
            else:
                messagebox.showerror("Error", "Event monitor not available")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply interval: {e}")
    
    def _save_settings(self):
        """Save application settings"""
        try:
            # Handle autostart setting
            autostart_enabled = self.autostart_var.get()
            current_status = is_autostart_enabled()
            
            if autostart_enabled != current_status:
                success = toggle_autostart(autostart_enabled)
                if success:
                    status = "enabled" if autostart_enabled else "disabled"
                    messagebox.showinfo("Settings", f"Settings saved successfully. Autostart {status}.")
                else:
                    messagebox.showerror("Error", "Failed to update autostart setting")
            else:
                messagebox.showinfo("Settings", "Settings saved successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _refresh_logs(self):
        """Refresh the log display"""
        try:
            # Find the most recent log file
            logs_dir = Path("logs")
            if not logs_dir.exists():
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(1.0, "Logs directory not found")
                return
            
            # Look for log files with pattern desktop_manager_YYYYMMDD.log
            log_files = list(logs_dir.glob("desktop_manager_*.log"))
            if not log_files:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(1.0, "No log files found")
                return
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(1.0, content)
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(1.0, f"Error loading logs: {e}")
    
    def _clear_logs(self):
        """Clear the log file"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            try:
                logs_dir = Path("logs")
                if logs_dir.exists():
                    # Clear all log files
                    log_files = list(logs_dir.glob("desktop_manager_*.log"))
                    for log_file in log_files:
                        log_file.unlink()
                    messagebox.showinfo("Success", f"Cleared {len(log_files)} log files")
                self._refresh_logs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def _start_monitoring(self):
        """Start the event monitoring in a separate thread"""
        def monitor_thread():
            self.event_monitor.start()
        
        self.monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitor_thread.start()
        
        # Start system tray
        if self.system_tray:
            self.system_tray.start()
        
        # Start stats update thread
        def stats_thread():
            while True:
                self._update_stats()
                time.sleep(1)
        
        self.stats_thread = threading.Thread(target=stats_thread, daemon=True)
        self.stats_thread.start()
    
    def _update_stats(self):
        """Update statistics display"""
        try:
            # Get CPU usage
            cpu_stats = get_cpu_stats()
            cpu_percent = cpu_stats["current"]
            self.stats["cpu_usage"] = cpu_percent
            
            # Update stats from rule engine
            if hasattr(self, 'rule_engine') and self.rule_engine:
                engine_stats = self.rule_engine.get_statistics()
                self.stats["events_processed"] = engine_stats.get("total_events_processed", 0)
                self.stats["rules_triggered"] = engine_stats.get("total_rules_executed", 0)
                self.stats["windows_managed"] = engine_stats.get("current_windows_tracked", 0)
            
            # Update display
            self.events_label.config(text=str(self.stats["events_processed"]))
            self.rules_label.config(text=str(self.stats["rules_triggered"]))
            self.windows_label.config(text=str(self.stats["windows_managed"]))
            self.cpu_label.config(text=f"{cpu_percent:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")
    
    def show_window(self):
        """Show the main window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_window(self):
        """Hide the main window to system tray"""
        if self.system_tray:
            self.system_tray.hide_window()
        else:
            self.root.withdraw()
    
    def quit_app(self):
        """Quit the application"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit Desktop Manager?"):
            if self.system_tray:
                self.system_tray.stop()
            if self.event_monitor:
                self.event_monitor.stop()
            self.root.quit()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run() 