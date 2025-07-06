"""
Package information for Desktop Manager
This file contains version and metadata used by the installer
"""

# Version information
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_BUILD = 0

# Application metadata
APP_NAME = "Desktop Manager Pro"
APP_DESCRIPTION = "A professional Windows desktop management application with modern UI and advanced rule-based automation"
COMPANY_NAME = "Desktop Manager"
COPYRIGHT = "Copyright (c) 2024 Desktop Manager"

# URLs
HELP_URL = "https://github.com/yourusername/desktop-manager"
UPDATE_URL = "https://github.com/yourusername/desktop-manager"
ABOUT_URL = "https://github.com/yourusername/desktop-manager"

# Installation settings
INSTALL_SIZE = 50000  # Estimated size in KB
MIN_WINDOWS_VERSION = "10.0"

def get_version_string():
    """Get the full version string"""
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}.{VERSION_BUILD}"

def get_version_tuple():
    """Get the version as a tuple"""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_BUILD) 