"""
BLUX Guard CLI Widgets
Textual UI components for security monitoring
"""

# Import available widgets
from .anti_tamper_controls import AntiTamperControls
from .decisions_view import DecisionsView
from .dev_menu_tree import DevMenuTree
from .logs_view import LogsView
from .network_monitor import NetworkMonitor
from .process_monitor import ProcessMonitor
from .scripts_view import ScriptsView
from .sensors_dashboard import SensorsDashboard
from .tree import Tree

# Note: CockpitHeaderFooter is not available in current widgets

__all__ = [
    'AntiTamperControls',
    'DecisionsView', 
    'DevMenuTree',
    'LogsView',
    'NetworkMonitor',
    'ProcessMonitor',
    'ScriptsView',
    'SensorsDashboard',
    'Tree'
]
