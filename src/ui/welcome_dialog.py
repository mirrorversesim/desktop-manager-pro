"""
Welcome dialog for Desktop Manager Pro
Shows user agreement and trust notice
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import json


class WelcomeDialog:
    """Welcome dialog with user agreement"""
    
    def __init__(self, parent):
        self.parent = parent
        self.accepted = False
        self.dialog = None
        
        # Check if user has already accepted
        self.agreement_file = Path("config/user_agreement_accepted.json")
        if self.agreement_file.exists():
            try:
                with open(self.agreement_file, 'r') as f:
                    data = json.load(f)
                    if data.get("accepted", False):
                        self.accepted = True
                        return
            except:
                pass
    
    def show(self):
        """Show the welcome dialog"""
        if self.accepted:
            return True
            
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        self.dialog = dialog
        dialog.title("Welcome to Desktop Manager Pro")
        dialog.geometry("650x480")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.focus_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (dialog.winfo_screenheight() // 2) - (480 // 2)
        dialog.geometry(f"650x480+{x}+{y}")
        
        # Main container
        container = tk.Frame(dialog, bg="#ECF0F1")
        container.pack(fill="both", expand=True)
        
        # Canvas for scrollable content
        canvas = tk.Canvas(container, bg="#ECF0F1", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add vertical scrollbar
        vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        vscroll.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=vscroll.set)
        
        # Frame inside canvas
        content_frame = tk.Frame(canvas, bg="#ECF0F1")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Bind resizing to update scrollregion
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind("<Configure>", on_configure)
        
        # Header
        header_frame = tk.Frame(content_frame, bg="#2C3E50", height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Welcome to Desktop Manager Pro", 
                              font=("Segoe UI", 18, "bold"), 
                              bg="#2C3E50", fg="white")
        title_label.pack(pady=20)
        
        # Important notice
        notice_frame = tk.LabelFrame(content_frame, text="Important Information", 
                                    font=("Segoe UI", 12, "bold"), 
                                    bg="#ECF0F1", fg="#E74C3C")
        notice_frame.pack(fill="x", pady=(0, 20), padx=4)
        
        notice_text = (
            "This application is open-source and provided as-is. As an independent developer, this executable is "
            "not digitally signed with a code signing certificate.\n\n"
            "What this means:\n"
            "  • Windows may show an 'Unknown Publisher' warning\n"
            "  • Your antivirus might flag it as potentially suspicious\n"
            "  • This is normal for unsigned software from independent developers\n\n"
            "Our commitment to transparency:\n"
            "  • Full source code available on GitHub\n"
            "  • No hidden functionality or data collection\n"
            "  • You can review the code to verify its safety\n"
            "  • Open-source nature ensures full transparency\n\n"
            "If you encounter warnings, you'll need to manually approve the execution. "
            "This is safe and expected for unsigned open-source software."
        )
        
        notice_label = tk.Label(
            notice_frame,
            text=notice_text,
            font=("Segoe UI", 10),
            bg="#ECF0F1",
            fg="#2C3E50",
            wraplength=600,
            justify="left",
            anchor="w",
            padx=8,
            pady=8
        )
        notice_label.pack(fill="x", padx=8, pady=8)
        
        # License agreement
        license_frame = tk.LabelFrame(content_frame, text="License Agreement", 
                                     font=("Segoe UI", 12, "bold"), 
                                     bg="#ECF0F1", fg="#2C3E50")
        license_frame.pack(fill="both", expand=True, pady=(0, 20), padx=4)
        
        # Create text widget with scrollbar for license
        text_frame = tk.Frame(license_frame, bg="#ECF0F1")
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        license_text_widget = tk.Text(text_frame, font=("Segoe UI", 9), 
                                     bg="#FFFFFF", fg="#2C3E50",
                                     wrap="word", height=8, state="normal")
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=license_text_widget.yview)
        license_text_widget.configure(yscrollcommand=scrollbar.set)
        
        license_text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # License text
        license_text = (
            "Desktop Manager Pro - License Agreement\n\n"
            "Copyright (c) 2025 Desktop Manager\n\n"
            "This software is provided 'as is' without warranty of any kind.\n\n"
            "Commercial Use:\n"
            "  • You may use this software for commercial purposes\n"
            "  • You may distribute this software as part of your products\n"
            "  • Attribution is appreciated but not required\n\n"
            "Limitations:\n"
            "  • The software is provided without warranty\n"
            "  • The author is not liable for any damages\n"
            "  • Use at your own risk\n\n"
            "Open Source:\n"
            "  • Full source code available on GitHub\n"
            "  • You can modify and distribute the source code\n"
            "  • Contributions are welcome\n\n"
            "Support:\n"
            "  • Basic support provided through GitHub issues\n"
            "  • Premium support available for commercial users\n"
            "  • Community support through GitHub discussions\n\n"
            "By using this software, you agree to these terms."
        )
        
        license_text_widget.insert("1.0", license_text)
        license_text_widget.config(state="disabled")
        
        # Fixed button bar at the bottom
        button_bar = tk.Frame(dialog, bg="#ECF0F1")
        button_bar.pack(fill="x", side="bottom", pady=(0, 12))
        
        # Decline button
        decline_btn = tk.Button(button_bar, text="Decline and Exit", 
                               command=lambda: self._handle_response(dialog, False),
                               font=("Segoe UI", 10, "bold"), bg="#E74C3C", fg="white",
                               relief="flat", padx=24, pady=10)
        decline_btn.pack(side="left", padx=(32, 10))
        
        # Accept button
        accept_btn = tk.Button(button_bar, text="I Accept and Continue", 
                              command=lambda: self._handle_response(dialog, True),
                              font=("Segoe UI", 10, "bold"), bg="#27AE60", fg="white",
                              relief="flat", padx=24, pady=10)
        accept_btn.pack(side="right", padx=(10, 32))
        
        # Focus on accept button
        accept_btn.focus_set()
        
        # Wait for user response
        dialog.wait_window()
        
        return self.accepted
    
    def _handle_response(self, dialog, accepted):
        """Handle user response"""
        if accepted:
            # Save acceptance
            self._save_acceptance()
            self.accepted = True
            dialog.destroy()
        else:
            # Show message and close app
            messagebox.showinfo("Goodbye", 
                              "You must accept the license agreement to use Desktop Manager Pro.\n\n"
                              "The application will now close.")
            dialog.destroy()
            self.parent.quit()
    
    def _save_acceptance(self):
        """Save that user accepted the agreement"""
        try:
            # Create config directory if it doesn't exist
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            # Save acceptance
            data = {
                "accepted": True,
                "accepted_date": "2025-01-07",
                "version": "1.0.0"
            }
            
            with open(self.agreement_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            # If we can't save, that's okay - just log it
            pass


def show_welcome_dialog(parent):
    """Show the welcome dialog and return True if accepted"""
    dialog = WelcomeDialog(parent)
    return dialog.show() 