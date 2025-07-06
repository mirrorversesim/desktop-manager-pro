# Desktop Manager Pro 🖥️

A powerful Windows desktop management application that provides intelligent window management, rule-based automation, performance monitoring, and system tray integration.

![Desktop Manager Pro](assets/icon.ico)

## ✨ Features

### 🎯 Smart Window Management
- **Automatic window positioning** based on custom rules
- **Multi-monitor support** with intelligent window placement
- **Window snapping** and organization
- **Custom window layouts** for different workflows

### 🤖 Rule-Based Automation
- **Event-driven automation** - respond to window events automatically
- **Custom rule creation** with an intuitive editor
- **Conditional actions** based on window properties
- **Scheduled tasks** and time-based automation

### 📊 Performance Monitoring
- **Real-time system monitoring** (CPU, RAM, disk usage)
- **Process tracking** and resource analysis
- **Performance alerts** and notifications
- **Historical data** and trend analysis

### 🔧 System Integration
- **System tray integration** with quick access menu
- **Autostart support** - launch with Windows
- **Background operation** with minimal resource usage
- **User agreement compliance** for transparency

### 🎨 Modern UI
- **Clean, intuitive interface** built with tkinter
- **Dark/light theme support**
- **Responsive design** that adapts to screen size
- **Accessible controls** for all users

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- Administrator privileges (for autostart features)

### Installation

#### Option 1: Portable Executable (Recommended)
1. Download `DesktopManagerPro.exe` from releases
2. Run the executable - no installation required
3. Accept the user agreement when prompted
4. The app will start in system tray

#### Option 2: Installer
1. Download `DesktopManager-Setup.exe` from releases
2. Run the installer with administrator privileges
3. Follow the installation wizard
4. Desktop Manager Pro will be installed and added to autostart

#### Option 3: From Source
```bash
# Clone the repository
git clone https://github.com/[YOUR_USERNAME]/desktop-manager-pro.git
cd desktop-manager-pro

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📖 Usage Guide

### First Launch
1. **User Agreement**: Accept the terms to continue
2. **System Tray**: The app minimizes to system tray automatically
3. **Configuration**: Access settings via the tray icon context menu

### Creating Rules
1. Open the **Rule Editor** from the main window
2. Define **conditions** (window title, process name, etc.)
3. Set **actions** (move, resize, minimize, etc.)
4. **Save and activate** your rules

### Performance Monitoring
- View real-time metrics in the **Performance** tab
- Set up **alerts** for resource thresholds
- Export **reports** for analysis

### System Tray Features
- **Right-click** the tray icon for quick access
- **Double-click** to restore the main window
- **Context menu** provides all main functions

## 🛠️ Configuration

### Rule Configuration
Rules are stored in `config/default_rules.json` and can be customized:

```json
{
  "rules": [
    {
      "name": "Move Chrome to Monitor 2",
      "conditions": {
        "process_name": "chrome.exe"
      },
      "actions": [
        {
          "type": "move",
          "x": 1920,
          "y": 0
        }
      ]
    }
  ]
}
```

### Performance Settings
- **Monitoring intervals** can be adjusted
- **Alert thresholds** are customizable
- **Data retention** periods can be modified

## 🔧 Development

### Project Structure
```
desktop_manager/
├── src/
│   ├── core/           # Core functionality
│   ├── ui/            # User interface components
│   ├── rules/         # Rule engine and automation
│   └── utils/         # Utility functions
├── config/            # Configuration files
├── assets/            # Icons and resources
├── tests/             # Test files
└── logs/              # Application logs
```

### Building from Source
```bash
# Build executable
python build_exe.py

# Build installer
python build_installer.py
```

### Dependencies
- `tkinter` - GUI framework
- `psutil` - System monitoring
- `pystray` - System tray integration
- `Pillow` - Image processing
- `pywin32` - Windows API integration

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Bug Reports

Please use the [GitHub Issues](https://github.com/yourusername/desktop-manager-pro/issues) page to report bugs or request features.

## 📞 Support

- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the [Wiki](https://github.com/yourusername/desktop-manager-pro/wiki) for detailed guides
- **Releases**: Download the latest version from [Releases](https://github.com/yourusername/desktop-manager-pro/releases)

## 🎯 Roadmap

- [ ] **Plugin system** for custom extensions
- [ ] **Cloud sync** for rules and settings
- [ ] **Advanced automation** with scripting support
- [ ] **Mobile companion app** for remote management
- [ ] **Multi-language support**

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/desktop-manager-pro&type=Date)](https://star-history.com/#yourusername/desktop-manager-pro&Date)

---

**Made with ❤️ for Windows users who want to take control of their desktop experience.**

*Desktop Manager Pro - Your desktop, your rules.* 