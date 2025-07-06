#!/usr/bin/env python3
"""
Build script for Desktop Manager installer
Creates a standalone executable and packages it into an installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def create_executable():
    """Create standalone executable using PyInstaller"""
    print("Creating standalone executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",  # No console window
        "--name=DesktopManagerPro",
        "--icon=assets/icon.ico",  # We'll create this
        "--add-data=config;config",  # Include config files
        "--hidden-import=win32gui",
        "--hidden-import=win32con",
        "--hidden-import=win32process",
        "--hidden-import=win32api",
        "--hidden-import=psutil",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "run_pro.py"
    ]
    
    return run_command(cmd)

def create_icon():
    """Create a simple icon for the application"""
    print("Creating application icon...")
    
    # Create assets directory
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple icon using PIL
    try:
        from PIL import Image, ImageDraw
        
        # Create a 256x256 icon
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple window icon
        margin = 20
        window_width = size - 2 * margin
        window_height = size - 2 * margin
        
        # Window background
        draw.rectangle([margin, margin, margin + window_width, margin + window_height], 
                      fill=(70, 130, 180), outline=(50, 100, 150), width=3)
        
        # Title bar
        title_height = 30
        draw.rectangle([margin, margin, margin + window_width, margin + title_height], 
                      fill=(100, 150, 200), outline=(50, 100, 150), width=2)
        
        # Window controls (minimize, maximize, close)
        control_size = 8
        control_y = margin + title_height // 2 - control_size // 2
        
        # Close button (red)
        close_x = margin + window_width - 25
        draw.ellipse([close_x, control_y, close_x + control_size, control_y + control_size], 
                    fill=(220, 80, 80))
        
        # Maximize button (yellow)
        max_x = close_x - 20
        draw.ellipse([max_x, control_y, max_x + control_size, control_y + control_size], 
                    fill=(220, 200, 80))
        
        # Minimize button (green)
        min_x = max_x - 20
        draw.ellipse([min_x, control_y, min_x + control_size, control_y + control_size], 
                    fill=(80, 220, 80))
        
        # Save as ICO
        icon_path = assets_dir / "icon.ico"
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"Icon created: {icon_path}")
        
    except ImportError:
        print("PIL not available, skipping icon creation")
        return False
    
    return True

def create_nsis_script():
    """Create NSIS installer script"""
    print("Creating NSIS installer script...")
    
    nsis_script = """# Desktop Manager Pro Installer Script
!define APPNAME "Desktop Manager Pro"
!define COMPANYNAME "Desktop Manager"
!define DESCRIPTION "A professional Windows desktop management application with modern UI and advanced rule-based automation"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/desktop-manager"
!define UPDATEURL "https://github.com/yourusername/desktop-manager"
!define ABOUTURL "https://github.com/yourusername/desktop-manager"
!define INSTALLSIZE 50000

RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

InstallDir "$PROGRAMFILES\\${APPNAME}"
LicenseData "LICENSE.txt"
Name "${APPNAME}"
Icon "assets\\icon.ico"
outFile "DesktopManager-Setup.exe"

!include LogicLib.nsh

page license
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        quit
${EndIf}
!macroend

function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

section "install"
	setOutPath $INSTDIR
	file "dist\\DesktopManagerPro.exe"
	file "config\\default_rules.json"
	
	# Create uninstaller
	writeUninstaller "$INSTDIR\\uninstall.exe"
	
	# Create start menu shortcut
	createDirectory "$SMPROGRAMS\\${APPNAME}"
	createShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\DesktopManagerPro.exe" "" "$INSTDIR\\DesktopManagerPro.exe"
	createShortCut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
	
	# Create desktop shortcut
	createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\DesktopManagerPro.exe" "" "$INSTDIR\\DesktopManagerPro.exe"
	
	# Write registry information for add/remove programs
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\" /S"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$INSTDIR"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayIcon" "$INSTDIR\\DesktopManager.exe"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "HelpLink" "${HELPURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
	
	# Create auto-start entry
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APPNAME}" "$INSTDIR\\DesktopManagerPro.exe"
	
	# Create logs directory
	createDirectory "$INSTDIR\\logs"
	
	# Set file permissions
	AccessControl::GrantOnFile "$INSTDIR\\logs" "(BU)" "FullAccess"
	
sectionEnd

section "uninstall"
	# Remove start menu items
	delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
	delete "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk"
	rmDir "$SMPROGRAMS\\${APPNAME}"
	
	# Remove desktop shortcut
	delete "$DESKTOP\\${APPNAME}.lnk"
	
	# Remove files and uninstaller
	delete $INSTDIR\\DesktopManagerPro.exe
	delete $INSTDIR\\default_rules.json
	delete $INSTDIR\\uninstall.exe
	
	# Remove logs directory
	rmDir /r "$INSTDIR\\logs"
	rmDir $INSTDIR
	
	# Remove registry keys
	DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
	DeleteRegValue HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APPNAME}"
	
	# Remove auto-start entry
	DeleteRegValue HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APPNAME}"
sectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    print("NSIS script created: installer.nsi")
    return True

def create_license():
    """Create a simple license file"""
    print("Creating license file...")
    
    license_text = """Desktop Manager License

Copyright (c) 2024 Your Company

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open("LICENSE.txt", "w") as f:
        f.write(license_text)
    
    print("License file created: LICENSE.txt")
    return True

def create_readme():
    """Create a README file for the installer"""
    print("Creating README file...")
    
    readme_text = """# Desktop Manager

A lightweight Windows background application to manage desktop windows and processes based on user-defined rules.

## Features

- **Window State Management**: Automatically minimize, close, or organize windows based on custom rules
- **Process Monitoring**: Track and manage running processes
- **Rule-Based Automation**: Define custom rules for window and process behavior
- **System Tray Interface**: Minimal UI with system tray integration
- **Low Resource Usage**: Optimized for background operation with minimal CPU usage

## Installation

1. Run the installer as Administrator
2. Choose installation directory
3. Desktop Manager will start automatically with Windows

## Usage

- Desktop Manager runs in the background automatically
- Access settings via the system tray icon
- View logs in the installation directory
- Configure rules in the config file

## System Requirements

- Windows 10 or later
- Administrator privileges for installation
- 50MB free disk space

## Support

For support and updates, visit: https://github.com/yourusername/desktop-manager

## License

This software is licensed under the MIT License. See LICENSE.txt for details.
"""
    
    with open("README.txt", "w") as f:
        f.write(readme_text)
    
    print("README file created: README.txt")
    return True

def main():
    """Main build process"""
    print("=== Desktop Manager Installer Build Process ===")
    
    # Check if we're in the right directory
    if not Path("run_background.pyw").exists():
        print("Error: run_background.pyw not found. Please run this script from the desktop_manager directory.")
        return False
    
    # Install dependencies
    print("Installing build dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        return False
    
    # Create icon
    create_icon()
    
    # Create executable
    if not create_executable():
        print("Failed to create executable")
        return False
    
    # Create installer files
    create_license()
    create_readme()
    create_nsis_script()
    
    print("\n=== Build Complete ===")
    print("Files created:")
    print("- dist/DesktopManagerPro.exe (standalone executable)")
    print("- installer.nsi (NSIS installer script)")
    print("- LICENSE.txt (license file)")
    print("- README.txt (readme file)")
    print("\nTo create the installer:")
    print("1. Install NSIS from https://nsis.sourceforge.io/")
    print("2. Run: makensis installer.nsi")
    print("3. The installer will be created as: DesktopManager-Setup.exe")
    
    return True

if __name__ == "__main__":
    main() 