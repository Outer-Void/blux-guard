"""
BLUX Guard CLI Package
======================

A cross-platform security monitoring and management CLI with TUI interface.
Supports Linux, WSL2, macOS, Termux, Android, and Windows environments.

Package Structure:
- blux.py: Main CLI entry point with security integration
- widgets/: Textual UI components and custom widgets
- security_integration.py: Unified security system

Features:
- Multi-environment compatibility
- Unified security system with authentication
- Real-time security monitoring
- Interactive TUI dashboard
- Cross-platform process management
- Extensible widget system
- Root privilege detection and fallbacks
"""

__version__ = "1.0.0"
__author__ = "Outer Void Team"
__description__ = "Cross-platform security monitoring CLI with TUI interface"

import os
import sys
import logging
from pathlib import Path

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

# Export main functions and classes for easy access
from .blux import main, detect_environment, find_python, setup_paths

# Security integration
try:
    from .security_integration import SecurityIntegration
except ImportError as e:
    logger.warning("Security integration not available: %s", e)
    SecurityIntegration = None  # or create a dummy class

# Widget classes (conditional)
AntiTamperControls = None
CockpitHeaderFooter = None
DecisionsView = None
DevMenuTree = None
LogsView = None
NetworkMonitor = None
ProcessMonitor = None
ScriptsView = None
SensorsDashboard = None
Tree = None

try:
    from .widgets import (
        AntiTamperControls,
        CockpitHeaderFooter,
        DecisionsView,
        DevMenuTree,
        LogsView,
        NetworkMonitor,
        ProcessMonitor,
        ScriptsView,
        SensorsDashboard,
        Tree
    )
except ImportError as e:
    logger.warning("Failed to import widgets: %s. Make sure textual is installed.", e)
    logger.info("To install textual, run: pip install textual")

# Configuration
class CLIConfig:
    """CLI configuration settings."""
    # Default paths
    REPO_ROOT = _project_root
    CONFIG_DIR = _project_root / ".config" / "blux_guard"
    LOGS_DIR = _project_root / "logs"
    
    # UI settings
    REFRESH_RATE = 1.0  # seconds
    MAX_LOG_LINES = 1000
    ENABLE_COLORS = True
    
    # Environment-specific settings
    if ENVIRONMENT in ["termux", "android"]:
        ENABLE_MOUSE = False
        MAX_WIDTH = 80
    else:
        ENABLE_MOUSE = True
        MAX_WIDTH = 120

def get_version():
    """Get the current version of the BLUX Guard CLI."""
    return __version__

def get_environment_info():
    """Get information about the current environment."""
    import platform
    return {
        "environment": ENVIRONMENT,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cli_version": __version__
    }

# Clean up namespace
del os, sys, Path

__all__ = [
    # Main functions
    'main',
    'detect_environment', 
    'find_python',
    'setup_paths',
    
    # Security
    'SecurityIntegration',
    
    # Configuration
    'CLIConfig',
    'get_version',
    'get_environment_info',
    
    # Constants
    'ENVIRONMENT',
    '__version__',
    '__author__',
    '__description__',
    
    # Widget classes (conditional)
    'AntiTamperControls',
    'CockpitHeaderFooter', 
    'DecisionsView',
    'DevMenuTree',
    'LogsView',
    'NetworkMonitor',
    'ProcessMonitor',
    'ScriptsView',
    'SensorsDashboard',
    'Tree'
]
