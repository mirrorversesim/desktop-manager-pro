"""
Rule Editor Dialog
Modern interface for creating and editing Desktop Manager rules
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable


class RuleEditorDialog:
    """Dialog for creating and editing rules"""
    
    def __init__(self, parent, rule_data: Optional[Dict[str, Any]] = None, 
                 on_save: Optional[Callable] = None):
        self.parent = parent
        self.rule_data = rule_data or {}
        self.on_save = on_save
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Rule" if rule_data else "New Rule")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#ECF0F1")
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create UI
        self._create_ui()
        
        # Load existing data
        if rule_data:
            self._load_rule_data()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
    
    def _create_ui(self):
        """Create the rule editor UI"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg="#ECF0F1")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#2C3E50", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Rule Editor", 
                              font=("Segoe UI", 18, "bold"), 
                              bg="#2C3E50", fg="white")
        title_label.pack(pady=15)
        
        # Create scrollable content
        canvas = tk.Canvas(main_frame, bg="#ECF0F1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#ECF0F1")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form sections
        self._create_basic_info_section()
        self._create_trigger_section()
        self._create_conditions_section()
        self._create_action_section()
        self._create_advanced_section()
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_basic_info_section(self):
        """Create basic rule information section"""
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Basic Information", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        section_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Rule name
        name_frame = tk.Frame(section_frame, bg="#ECF0F1")
        name_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(name_frame, text="Rule Name:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.name_entry = tk.Entry(name_frame, font=("Segoe UI", 10), 
                                  bg="white", fg="#2C3E50", relief="flat", bd=1)
        self.name_entry.pack(fill="x", pady=(5, 0))
        
        # Description
        desc_frame = tk.Frame(section_frame, bg="#ECF0F1")
        desc_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(desc_frame, text="Description:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.desc_text = tk.Text(desc_frame, height=3, font=("Segoe UI", 10), 
                                bg="white", fg="#2C3E50", relief="flat", bd=1, wrap="word")
        self.desc_text.pack(fill="x", pady=(5, 0))
        
        # Enabled checkbox
        enabled_frame = tk.Frame(section_frame, bg="#ECF0F1")
        enabled_frame.pack(fill="x", padx=15, pady=10)
        
        self.enabled_var = tk.BooleanVar(value=True)
        enabled_check = tk.Checkbutton(enabled_frame, text="Rule Enabled", 
                                      variable=self.enabled_var, font=("Segoe UI", 10),
                                      bg="#ECF0F1", fg="#2C3E50")
        enabled_check.pack(anchor="w")
    
    def _create_trigger_section(self):
        """Create trigger configuration section"""
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Trigger", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        section_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Trigger type
        trigger_frame = tk.Frame(section_frame, bg="#ECF0F1")
        trigger_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(trigger_frame, text="Trigger Type:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.trigger_var = tk.StringVar(value="window_created")
        trigger_combo = ttk.Combobox(trigger_frame, textvariable=self.trigger_var, 
                                    font=("Segoe UI", 10), state="readonly")
        trigger_combo['values'] = [
            "window_created",
            "window_focused", 
            "window_closed",
            "process_started",
            "process_ended",
            "file_opened",
            "folder_opened"
        ]
        trigger_combo.pack(fill="x", pady=(5, 0))
        
        # Target application
        target_frame = tk.Frame(section_frame, bg="#ECF0F1")
        target_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(target_frame, text="Target Application:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.target_entry = tk.Entry(target_frame, font=("Segoe UI", 10), 
                                    bg="white", fg="#2C3E50", relief="flat", bd=1)
        self.target_entry.pack(fill="x", pady=(5, 0))
        
        # Help text
        help_label = tk.Label(target_frame, text="Enter process name (e.g., notepad.exe) or leave empty for all applications", 
                             font=("Segoe UI", 8), bg="#ECF0F1", fg="#7F8C8D")
        help_label.pack(anchor="w", pady=(2, 0))
    
    def _create_conditions_section(self):
        """Create conditions section"""
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Conditions", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        section_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Window title condition
        title_frame = tk.Frame(section_frame, bg="#ECF0F1")
        title_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(title_frame, text="Window Title Contains:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.title_entry = tk.Entry(title_frame, font=("Segoe UI", 10), 
                                   bg="white", fg="#2C3E50", relief="flat", bd=1)
        self.title_entry.pack(fill="x", pady=(5, 0))
        
        # Window count condition
        count_frame = tk.Frame(section_frame, bg="#ECF0F1")
        count_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(count_frame, text="Maximum Windows:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        count_input_frame = tk.Frame(count_frame, bg="#ECF0F1")
        count_input_frame.pack(fill="x", pady=(5, 0))
        
        self.count_var = tk.StringVar(value="1")
        count_spinbox = tk.Spinbox(count_input_frame, from_=1, to=100, 
                                  textvariable=self.count_var, font=("Segoe UI", 10),
                                  bg="white", fg="#2C3E50", relief="flat", bd=1, width=10)
        count_spinbox.pack(side="left")
        
        tk.Label(count_input_frame, text="(0 = unlimited)", font=("Segoe UI", 8), 
                bg="#ECF0F1", fg="#7F8C8D").pack(side="left", padx=(10, 0))
    
    def _create_action_section(self):
        """Create action configuration section"""
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Action", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        section_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Action type
        action_frame = tk.Frame(section_frame, bg="#ECF0F1")
        action_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(action_frame, text="Action Type:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.action_var = tk.StringVar(value="minimize_others")
        action_combo = ttk.Combobox(action_frame, textvariable=self.action_var, 
                                   font=("Segoe UI", 10), state="readonly")
        action_combo['values'] = [
            "minimize_others",
            "close_others",
            "close_oldest",
            "close_newest",
            "bring_to_front",
            "minimize_window",
            "maximize_window",
            "restore_window"
        ]
        action_combo.pack(fill="x", pady=(5, 0))
        
        # Action parameters
        params_frame = tk.Frame(section_frame, bg="#ECF0F1")
        params_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(params_frame, text="Action Parameters:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.params_text = tk.Text(params_frame, height=3, font=("Segoe UI", 10), 
                                  bg="white", fg="#2C3E50", relief="flat", bd=1, wrap="word")
        self.params_text.pack(fill="x", pady=(5, 0))
        
        # Help text
        help_label = tk.Label(params_frame, text="Additional parameters in JSON format (optional)", 
                             font=("Segoe UI", 8), bg="#ECF0F1", fg="#7F8C8D")
        help_label.pack(anchor="w", pady=(2, 0))
    
    def _create_advanced_section(self):
        """Create advanced settings section"""
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Advanced Settings", 
                                     font=("Segoe UI", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        section_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Priority
        priority_frame = tk.Frame(section_frame, bg="#ECF0F1")
        priority_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(priority_frame, text="Priority:", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.priority_var = tk.StringVar(value="normal")
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var, 
                                     font=("Segoe UI", 10), state="readonly")
        priority_combo['values'] = ["low", "normal", "high", "critical"]
        priority_combo.pack(fill="x", pady=(5, 0))
        
        # Delay
        delay_frame = tk.Frame(section_frame, bg="#ECF0F1")
        delay_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(delay_frame, text="Delay (seconds):", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.delay_var = tk.StringVar(value="0.0")
        delay_spinbox = tk.Spinbox(delay_frame, from_=0.0, to=60.0, increment=0.1,
                                  textvariable=self.delay_var, font=("Segoe UI", 10),
                                  bg="white", fg="#2C3E50", relief="flat", bd=1, width=10)
        delay_spinbox.pack(side="left", pady=(5, 0))
        
        # Cooldown
        cooldown_frame = tk.Frame(section_frame, bg="#ECF0F1")
        cooldown_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(cooldown_frame, text="Cooldown (seconds):", font=("Segoe UI", 10), 
                bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        self.cooldown_var = tk.StringVar(value="1.0")
        cooldown_spinbox = tk.Spinbox(cooldown_frame, from_=0.0, to=3600.0, increment=0.1,
                                     textvariable=self.cooldown_var, font=("Segoe UI", 10),
                                     bg="white", fg="#2C3E50", relief="flat", bd=1, width=10)
        cooldown_spinbox.pack(side="left", pady=(5, 0))
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg="#ECF0F1")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Save button
        save_btn = tk.Button(button_frame, text="Save Rule", 
                            command=self._save_rule,
                            font=("Segoe UI", 10, "bold"), bg="#27AE60", fg="white",
                            relief="flat", padx=20, pady=8)
        save_btn.pack(side="right", padx=(10, 0))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self._cancel,
                              font=("Segoe UI", 10), bg="#95A5A6", fg="white",
                              relief="flat", padx=20, pady=8)
        cancel_btn.pack(side="right")
        
        # Test button
        test_btn = tk.Button(button_frame, text="Test Rule", 
                            command=self._test_rule,
                            font=("Segoe UI", 10), bg="#3498DB", fg="white",
                            relief="flat", padx=20, pady=8)
        test_btn.pack(side="left")
    
    def _load_rule_data(self):
        """Load existing rule data into the form"""
        try:
            # Basic info
            self.name_entry.insert(0, self.rule_data.get("name", ""))
            self.desc_text.insert("1.0", self.rule_data.get("description", ""))
            self.enabled_var.set(self.rule_data.get("enabled", True))
            
            # Trigger
            trigger = self.rule_data.get("trigger", {})
            self.trigger_var.set(trigger.get("type", "window_created"))
            self.target_entry.insert(0, trigger.get("target", ""))
            
            # Conditions
            conditions = self.rule_data.get("conditions", {})
            self.title_entry.insert(0, conditions.get("title_contains", ""))
            self.count_var.set(str(conditions.get("max_windows", 1)))
            
            # Action
            action = self.rule_data.get("action", {})
            self.action_var.set(action.get("type", "minimize_others"))
            
            params = action.get("parameters", {})
            if params:
                import json
                self.params_text.insert("1.0", json.dumps(params, indent=2))
            
            # Advanced
            self.priority_var.set(self.rule_data.get("priority", "normal"))
            self.delay_var.set(str(self.rule_data.get("delay", 0.0)))
            self.cooldown_var.set(str(self.rule_data.get("cooldown", 1.0)))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rule data: {e}")
    
    def _save_rule(self):
        """Save the rule data"""
        try:
            # Validate required fields
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Rule name is required")
                return
            
            # Build rule data
            rule_data = {
                "name": name,
                "description": self.desc_text.get("1.0", tk.END).strip(),
                "enabled": self.enabled_var.get(),
                "trigger": {
                    "type": self.trigger_var.get(),
                    "target": self.target_entry.get().strip()
                },
                "conditions": {
                    "title_contains": self.title_entry.get().strip(),
                    "max_windows": int(self.count_var.get())
                },
                "action": {
                    "type": self.action_var.get(),
                    "parameters": {}
                },
                "priority": self.priority_var.get(),
                "delay": float(self.delay_var.get()),
                "cooldown": float(self.cooldown_var.get())
            }
            
            # Parse action parameters
            params_text = self.params_text.get("1.0", tk.END).strip()
            if params_text:
                import json
                try:
                    rule_data["action"]["parameters"] = json.loads(params_text)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Invalid JSON in action parameters")
                    return
            
            # Call save callback
            if self.on_save:
                self.on_save(rule_data)
            
            self.result = rule_data
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save rule: {e}")
    
    def _test_rule(self):
        """Test the current rule configuration"""
        messagebox.showinfo("Test Rule", "Rule testing functionality would be implemented here")
    
    def _cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog and return the result"""
        self.dialog.wait_window()
        return self.result


def show_rule_editor(parent, rule_data=None, on_save=None):
    """Show the rule editor dialog"""
    dialog = RuleEditorDialog(parent, rule_data, on_save)
    return dialog.show() 