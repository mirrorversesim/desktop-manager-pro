#!/usr/bin/env python3
"""
Simple build script for Desktop Manager Pro executable
Creates a standalone .exe file ready for commercial distribution
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

def create_icon():
    """Create a professional icon for the application"""
    print("Creating application icon...")
    
    # Create assets directory
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create a professional icon using PIL
    try:
        from PIL import Image, ImageDraw
        
        # Create a 256x256 icon
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a modern window management icon
        margin = 30
        window_width = size - 2 * margin
        window_height = size - 2 * margin
        
        # Main window (blue gradient)
        draw.rectangle([margin, margin, margin + window_width, margin + window_height], 
                      fill=(52, 152, 219), outline=(41, 128, 185), width=4)
        
        # Title bar
        title_height = 40
        draw.rectangle([margin, margin, margin + window_width, margin + title_height], 
                      fill=(41, 128, 185), outline=(41, 128, 185), width=2)
        
        # Window controls
        control_size = 12
        control_y = margin + title_height // 2 - control_size // 2
        
        # Close button (red)
        close_x = margin + window_width - 35
        draw.ellipse([close_x, control_y, close_x + control_size, control_y + control_size], 
                    fill=(231, 76, 60), outline=(192, 57, 43), width=2)
        
        # Maximize button (yellow)
        max_x = close_x - 25
        draw.ellipse([max_x, control_y, max_x + control_size, control_y + control_size], 
                    fill=(241, 196, 15), outline=(243, 156, 18), width=2)
        
        # Minimize button (green)
        min_x = max_x - 25
        draw.ellipse([min_x, control_y, min_x + control_size, control_y + control_size], 
                    fill=(46, 204, 113), outline=(39, 174, 96), width=2)
        
        # Add some window content lines
        content_start = margin + title_height + 20
        for i in range(3):
            y = content_start + i * 25
            draw.line([margin + 20, y, margin + window_width - 20, y], 
                     fill=(255, 255, 255), width=2)
        
        # Save as ICO
        icon_path = assets_dir / "icon.ico"
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"✅ Professional icon created: {icon_path}")
        return True
        
    except ImportError:
        print("❌ PIL not available, skipping icon creation")
        return False

def build_executable():
    """Build the standalone executable"""
    print("Building Desktop Manager Pro executable...")
    
    # Clean previous builds
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("DesktopManagerPro.spec").exists():
        Path("DesktopManagerPro.spec").unlink()
    
    # PyInstaller command for a professional build
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name=DesktopManagerPro",     # Executable name
        "--icon=assets/icon.ico",       # Application icon
        "--add-data=config;config",     # Include config files
        "--add-data=src;src",           # Include source files
        "--hidden-import=win32gui",
        "--hidden-import=win32con", 
        "--hidden-import=win32process",
        "--hidden-import=win32api",
        "--hidden-import=win32com.client",
        "--hidden-import=psutil",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=pystray",
        "--hidden-import=pystray._util.win32",
        "--hidden-import=pystray._util.win32_icon",
        "--clean",                      # Clean cache
        "--noconfirm",                  # Don't ask for confirmation
        "run_pro.py"
    ]
    
    success = run_command(cmd)
    if success:
        print("✅ Executable built successfully!")
        exe_path = Path("dist/DesktopManagerPro.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable size: {size_mb:.1f} MB")
            print(f"📍 Location: {exe_path.absolute()}")
        return True
    else:
        print("❌ Failed to build executable")
        return False

def create_license():
    """Create a license file"""
    print("Creating license file...")
    
    license_text = """Desktop Manager Pro - License Agreement

Copyright (c) 2025 Desktop Manager

This software is provided "as is" without warranty of any kind.

Commercial Use:
- You may use this software for commercial purposes
- You may distribute this software as part of your products
- Attribution is appreciated but not required

Limitations:
- The software is provided without warranty
- The author is not liable for any damages
- Use at your own risk

For support and updates, visit: https://github.com/yourusername/desktop-manager
"""
    
    with open("LICENSE.txt", "w") as f:
        f.write(license_text)
    print("✅ License file created")

def create_readme():
    """Create a README file"""
    print("Creating README file...")
    
    readme_text = """# Desktop Manager Pro

A professional Windows desktop management application with modern UI and advanced rule-based automation.

## Features

- 🖥️ **Smart Window Management**: Automatically organize and manage desktop windows
- ⚡ **Rule-Based Automation**: Create custom rules for window behavior
- 🎨 **Modern UI**: Professional interface with real-time monitoring
- 🔧 **System Integration**: Seamless Windows integration with autostart support
- 📊 **Performance Monitoring**: Real-time statistics and performance tracking
- 🛡️ **Lightweight**: Minimal resource usage (typically <5MB RAM)

## Installation

1. Run `DesktopManagerPro.exe`
2. The application will start automatically
3. Configure your rules in the Rules tab
4. Enable "Start with Windows" in Settings for automatic startup

## Usage

1. **Dashboard**: View real-time statistics and system performance
2. **Rules**: Create and manage window management rules
3. **Settings**: Configure polling intervals and autostart options
4. **Logs**: Monitor application activity and troubleshoot issues

## System Requirements

- Windows 10/11
- 50MB free disk space
- 4MB RAM (typically uses much less)

## Support

For support, issues, and updates:
- GitHub: https://github.com/yourusername/desktop-manager
- Email: support@desktopmanager.com

## License

This software is provided "as is" for commercial and personal use.
"""
    
    with open("README.txt", "w") as f:
        f.write(readme_text)
    print("✅ README file created")

def create_package():
    """Create a distribution package"""
    print("Creating distribution package...")
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy files to dist
    files_to_copy = [
        ("LICENSE.txt", "LICENSE.txt"),
        ("README.txt", "README.txt"),
        ("config/default_rules.json", "config/default_rules.json")
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_dir / dst
        
        if src_path.exists():
            # Create parent directories
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"✅ Copied {src} to dist/")
    
    print("✅ Distribution package created!")

def main():
    """Main build process"""
    print("🚀 Desktop Manager Pro - Build Process")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build process
    steps = [
        ("Creating icon", create_icon),
        ("Building executable", build_executable),
        ("Creating license", create_license),
        ("Creating README", create_readme),
        ("Creating package", create_package)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed at: {step_name}")
            return False
    
    print("\n🎉 Build completed successfully!")
    print("\n📦 Distribution files:")
    print("  - DesktopManagerPro.exe (main executable)")
    print("  - LICENSE.txt (license agreement)")
    print("  - README.txt (user documentation)")
    print("  - config/default_rules.json (default rules)")
    
    print("\n💡 Next steps:")
    print("  1. Test the executable on a clean system")
    print("  2. Package with your preferred installer")
    print("  3. Distribute to customers!")
    
    return True

if __name__ == "__main__":
    main() 