"""
BLUX Guard CLI Widgets Package
Cross-platform UI components for BLUX Guard ecosystem
Version: 1.0.0
Author: Outer Void Team
"""

__version__ = "1.0.0"
__author__ = "Outer Void Team"
__description__ = "Cross-platform UI widgets for BLUX Guard"

import os
import sys
from pathlib import Path

# Add project root to path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Widget exports
try:
    from .tree import BLUXTree, TreeApp, SecurityStatus, NodeDetails, BasicTreeView
    TREE_AVAILABLE = True
except ImportError as e:
    TREE_AVAILABLE = False
    print(f"Tree widget not available: {e}")

try:
    from .anti_tamper_controls import AntiTamperControls
    ANTI_TAMPER_AVAILABLE = True
except ImportError:
    ANTI_TAMPER_AVAILABLE = False

try:
    from .cockpit_header_footer import CockpitHeaderFooter
    HEADER_FOOTER_AVAILABLE = True
except ImportError:
    HEADER_FOOTER_AVAILABLE = False

try:
    from .decisions_view import DecisionsView
    DECISIONS_AVAILABLE = True
except ImportError:
    DECISIONS_AVAILABLE = False

try:
    from .logs_view import LogsView
    LOGS_AVAILABLE = True
except ImportError:
    LOGS_AVAILABLE = False

try:
    from .network_monitor import NetworkMonitor
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False

try:
    from .process_monitor import ProcessMonitor
    PROCESS_AVAILABLE = True
except ImportError:
    PROCESS_AVAILABLE = False

try:
    from .sensors_dashboard import SensorsDashboard
    SENSORS_AVAILABLE = True
except ImportError:
    SENSORS_AVAILABLE = False

# Configuration
class WidgetConfig:
    """Widget configuration settings"""
    
    # UI Settings
    ENABLE_ANIMATIONS = True
    ENABLE_TOOLTIPS = True
    DEFAULT_THEME = "dark"
    
    # Security Settings
    SHOW_SECURITY_INDICATORS = True
    ENABLE_PRIVILEGE_CHECKS = True
    
    # Performance
    LAZY_LOAD_WIDGETS = True
    CACHE_WIDGET_STATES = True

def get_widget_availability():
    """Get availability status of all widgets"""
    return {
        'tree': TREE_AVAILABLE,
        'anti_tamper': ANTI_TAMPER_AVAILABLE,
        'header_footer': HEADER_FOOTER_AVAILABLE,
        'decisions': DECISIONS_AVAILABLE,
        'logs': LOGS_AVAILABLE,
        'network': NETWORK_AVAILABLE,
        'process': PROCESS_AVAILABLE,
        'sensors': SENSORS_AVAILABLE
    }

def create_fallback_widget(widget_name: str, message: str = None):
    """Create a fallback widget when main widget is unavailable"""
    from textual.widgets import Static
    
    class FallbackWidget(Static):
        def __init__(self):
            msg = message or f"Widget '{widget_name}' not available"
            super().__init__(f"⚠️ {msg}")
    
    return FallbackWidget()

# Clean up namespace
del os, sys, Path

__all__ = [
    # Tree widgets
    'BLUXTree', 'TreeApp', 'SecurityStatus', 'NodeDetails', 'BasicTreeView',
    
    # Other widgets (conditional)
    'AntiTamperControls',
    'CockpitHeaderFooter', 
    'DecisionsView',
    'LogsView',
    'NetworkMonitor',
    'ProcessMonitor',
    'SensorsDashboard',
    
    # Configuration
    'WidgetConfig',
    'get_widget_availability',
    'create_fallback_widget',
    
    # Constants
    '__version__',
    '__author__',
    '__description__'
]
