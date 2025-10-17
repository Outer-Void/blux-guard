"""
BLUX Guard Shell Package
========================

Interactive shell interface for BLUX Guard security system.
Provides menu-driven access to all BLUX Guard features with
cross-platform compatibility and security integration.

Features:
- Unified security system integration
- Cross-platform compatibility (Linux, macOS, Windows, Android, Termux)
- Privilege-aware functionality
- Rich terminal interface with fallbacks
- Emergency recovery options

Version: 1.0.0
Author: Outer Void Team
"""

__version__ = "1.0.0"
__author__ = "Outer Void Team"
__description__ = "Interactive shell interface for BLUX Guard security system"

import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path for module imports
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Environment detection
def detect_environment():
    """Detect the current operating environment."""
    import platform
    
    system = platform.system().lower()
    release = platform.release().lower()
    
    # Check for Android/Termux
    if hasattr(os, 'getppid') and 'termux' in os.environ.get('PREFIX', '').lower():
        return "termux"
    elif os.path.exists('/system/bin/adb') or os.path.exists('/system/app'):
        return "android"
    # Check for WSL
    elif 'microsoft' in release or 'wsl' in release:
        return "wsl2"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

# Package-level environment variable
ENVIRONMENT = detect_environment()

# Export main classes and functions
from .shell_menu import BLUXGuardShell, main

# Configuration
class ShellConfig:
    """Shell configuration settings."""
    
    # UI settings
    ENABLE_COLORS = True
    REFRESH_RATE = 1.0
    MAX_HISTORY = 100
    
    # Security settings
    REQUIRE_AUTHENTICATION = True
    MAX_AUTH_ATTEMPTS = 3
    ENABLE_EMERGENCY_RESET = True
    
    # Environment-specific settings
    if ENVIRONMENT in ["termux", "android"]:
        ENABLE_RICH_UI = False  # Simplified UI for mobile
        AUTO_START_MODULES = False
    else:
        ENABLE_RICH_UI = True
        AUTO_START_MODULES = True

def get_version():
    """Get the current version of the BLUX Guard Shell."""
    return __version__

def get_environment_info():
    """Get information about the current environment."""
    import platform
    return {
        "environment": ENVIRONMENT,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "shell_version": __version__
    }

def launch_shell():
    """Convenience function to launch the shell directly."""
    from .shell_menu import main as shell_main
    shell_main()

# Clean up namespace
del os, sys, Path

__all__ = [
    # Main classes
    'BLUXGuardShell',
    'main',
    'launch_shell',
    
    # Configuration
    'ShellConfig',
    'get_version',
    'get_environment_info',
    
    # Constants
    'ENVIRONMENT',
    '__version__',
    '__author__',
    '__description__'
]
