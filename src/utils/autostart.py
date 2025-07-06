"""
Autostart utilities for Desktop Manager
Handles Windows startup folder and registry entries
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


class AutostartManager:
    """Manages Windows autostart functionality"""
    
    def __init__(self, app_name: str = "Desktop Manager"):
        self.app_name = app_name
        self.startup_folder = self._get_startup_folder()
        self.registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def _get_startup_folder(self) -> Path:
        """Get the Windows startup folder path"""
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            startup_path = shell.SpecialFolders("Startup")
            return Path(startup_path)
        except Exception as e:
            logger.warning(f"Could not get startup folder via COM: {e}")
            # Fallback to default path
            return Path(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"))
    
    def _get_app_path(self) -> Optional[Path]:
        """Get the path to the current application"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys.executable)
        else:
            # Running as script
            script_path = Path(__file__).parent.parent.parent / "run_pro.py"
            if script_path.exists():
                return script_path
            return None
    
    def is_enabled(self) -> bool:
        """Check if autostart is enabled"""
        # Check startup folder
        app_path = self._get_app_path()
        if not app_path:
            return False
        
        shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
        if shortcut_path.exists():
            return True
        
        # Check registry
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key) as key:
                try:
                    winreg.QueryValueEx(key, self.app_name)
                    return True
                except FileNotFoundError:
                    pass
        except Exception as e:
            logger.warning(f"Could not check registry: {e}")
        
        return False
    
    def enable(self) -> bool:
        """Enable autostart"""
        try:
            app_path = self._get_app_path()
            if not app_path:
                logger.error("Could not determine application path")
                return False
            
            # Create startup folder if it doesn't exist
            self.startup_folder.mkdir(parents=True, exist_ok=True)
            
            # Create shortcut in startup folder
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
            
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(app_path)
                shortcut.WorkingDirectory = str(app_path.parent)
                shortcut.Description = f"Start {self.app_name} automatically"
                shortcut.save()
                logger.info(f"Created autostart shortcut: {shortcut_path}")
            except Exception as e:
                logger.warning(f"Could not create shortcut via COM: {e}")
                # Fallback: create a batch file
                batch_path = self.startup_folder / f"{self.app_name}.bat"
                with open(batch_path, 'w') as f:
                    f.write(f'@echo off\ncd /d "{app_path.parent}"\n"{app_path}"\n')
                logger.info(f"Created autostart batch file: {batch_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable(self) -> bool:
        """Disable autostart"""
        try:
            # Remove shortcut from startup folder
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
            if shortcut_path.exists():
                shortcut_path.unlink()
                logger.info(f"Removed autostart shortcut: {shortcut_path}")
            
            # Remove batch file if it exists
            batch_path = self.startup_folder / f"{self.app_name}.bat"
            if batch_path.exists():
                batch_path.unlink()
                logger.info(f"Removed autostart batch file: {batch_path}")
            
            # Remove registry entry
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_WRITE) as key:
                    try:
                        winreg.DeleteValue(key, self.app_name)
                        logger.info(f"Removed registry autostart entry: {self.app_name}")
                    except FileNotFoundError:
                        pass  # Entry doesn't exist
            except Exception as e:
                logger.warning(f"Could not remove registry entry: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable autostart: {e}")
            return False
    
    def toggle(self, enabled: bool) -> bool:
        """Toggle autostart on/off"""
        if enabled:
            return self.enable()
        else:
            return self.disable()


# Global instance
autostart_manager = AutostartManager()


def enable_autostart() -> bool:
    """Enable autostart for Desktop Manager"""
    return autostart_manager.enable()


def disable_autostart() -> bool:
    """Disable autostart for Desktop Manager"""
    return autostart_manager.disable()


def is_autostart_enabled() -> bool:
    """Check if autostart is enabled"""
    return autostart_manager.is_enabled()


def toggle_autostart(enabled: bool) -> bool:
    """Toggle autostart on/off"""
    return autostart_manager.toggle(enabled) 