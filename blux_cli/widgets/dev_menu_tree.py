# dev_menu_tree.py — BLUX Guard Cockpit (Universal Compatibility Patch)
"""
===============================================================
A stable Textual-based cockpit dashboard for system panels.
Compatible with Termux, WSL2, macOS, Linux, and Windows.
===============================================================
"""

import sys
import os
from pathlib import Path
from typing import Any

# Environment detection
def detect_environment():
    """Detect the current runtime environment."""
    if hasattr(sys, 'getandroidapilevel'):
        return "termux"
    elif 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False:
        return "wsl2"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32":
        return "windows"
    else:
        return "linux"

CURRENT_ENV = detect_environment()

# Import Textual with fallbacks
try:
    from textual.app import App, ComposeResult
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Static, Header, Footer
    from textual.reactive import reactive
    TEXTUAL_AVAILABLE = True
except ImportError as e:
    print(f"Textual import error: {e}")
    TEXTUAL_AVAILABLE = False

# Rich imports with fallbacks
try:
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Optional blux_cli imports with comprehensive error handling
blux_modules = {}
try:
    from blux_cli.widgets.network_monitor import NetworkMonitor, NetworkMonitorApp
    blux_modules['network_monitor'] = True
except ImportError as e:
    print(f"NetworkMonitor import failed: {e}")
    NetworkMonitor = NetworkMonitorApp = None
    blux_modules['network_monitor'] = False

try:
    from blux_cli.widgets.logs_viewer import LogsViewer
    blux_modules['logs_viewer'] = True
except ImportError as e:
    print(f"LogsViewer import failed: {e}")
    LogsViewer = None
    blux_modules['logs_viewer'] = False

try:
    from blux_cli.widgets.process_monitor import ProcessMonitor
    blux_modules['process_monitor'] = True
except ImportError as e:
    print(f"ProcessMonitor import failed: {e}")
    ProcessMonitor = None
    blux_modules['process_monitor'] = False

try:
    from blux_cli.widgets.sensors_dashboard import SensorsDashboard
    blux_modules['sensors_dashboard'] = True
except ImportError as e:
    print(f"SensorsDashboard import failed: {e}")
    SensorsDashboard = None
    blux_modules['sensors_dashboard'] = False

try:
    from blux_cli.widgets.decisions_view import DecisionsView
    blux_modules['decisions_view'] = True
except ImportError as e:
    print(f"DecisionsView import failed: {e}")
    DecisionsView = None
    blux_modules['decisions_view'] = False

try:
    from blux_cli.widgets.anti_tamper_controls import AntiTamperControls
    blux_modules['anti_tamper'] = True
except ImportError as e:
    print(f"AntiTamperControls import failed: {e}")
    AntiTamperControls = None
    blux_modules['anti_tamper'] = False

try:
    from blux_cli.widgets.scripts_view import ScriptsViewApp
    blux_modules['scripts_view'] = True
except ImportError as e:
    print(f"ScriptsViewApp import failed: {e}")
    ScriptsViewApp = None
    blux_modules['scripts_view'] = False


class FallbackDisplay:
    """Fallback display generator for missing modules."""
    
    def __init__(self, name, env):
        self.name = name
        self.env = env
    
    def generate_panel(self):
        if RICH_AVAILABLE:
            return Panel(
                f"[yellow]{self.name}[/yellow]\n"
                f"Environment: [cyan]{self.env}[/cyan]\n"
                f"Status: [red]Module not available[/red]\n\n"
                f"Install blux_cli or check dependencies.",
                title=f"⚠️ {self.name}",
                border_style="red"
            )
        return f"{self.name} - Not Available"

class SimpleNetworkMonitor:
    """Simple network monitor fallback"""
    def generate_panel(self):
        if RICH_AVAILABLE:
            return Panel(
                "[green]Network Status[/green]\n"
                f"Environment: {CURRENT_ENV}\n"
                "Basic network monitoring active",
                title="🌐 Network",
                border_style="green"
            )
        return "Network Monitor - Basic"

class SimpleProcessMonitor:
    """Simple process monitor fallback"""
    def generate_panel(self):
        if RICH_AVAILABLE:
            return Panel(
                "[green]Process Monitor[/green]\n"
                f"Environment: {CURRENT_ENV}\n"
                "Basic process monitoring active",
                title="⚙️ Processes", 
                border_style="blue"
            )
        return "Process Monitor - Basic"


class DevMenuTreeApp(App):
    """
    Main BLUX Guard cockpit visualization - Universal Compatibility Version.
    """

    # CSS path handling with fallback
    try:
        CSS_PATH = Path(__file__).parent / "blux_cockpit.css"
        if not CSS_PATH.exists():
            CSS_PATH = None
    except Exception:
        CSS_PATH = None

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle Dark Mode")]

    refresh_interval = reactive(5.0)  # Slower refresh for compatibility

    def __init__(self, **kwargs):
        if not TEXTUAL_AVAILABLE:
            print("ERROR: Textual framework not available.")
            print("Install with: pip install textual")
            sys.exit(1)
            
        super().__init__(**kwargs)
        
        # Environment-specific adjustments
        self._apply_environment_settings()
        
        # Initialize all panel objects with fallbacks
        self._initialize_panels()

    def _apply_environment_settings(self):
        """Apply settings based on detected environment."""
        if CURRENT_ENV == "termux":
            self.refresh_interval = 10.0  # Slower refresh for Termux
            print("Termux environment detected - optimizing for mobile")
        elif CURRENT_ENV == "wsl2":
            print("WSL2 environment detected")
        elif CURRENT_ENV == "macos":
            print("macOS environment detected") 

    def _initialize_panels(self):
        """Initialize all panel objects with proper fallbacks."""
        
        # Network Monitor
        try:
            if NetworkMonitor:
                self.network_obj = NetworkMonitor()
            elif NetworkMonitorApp:
                self.network_obj = NetworkMonitorApp()
            else:
                self.network_obj = SimpleNetworkMonitor()
        except Exception as e:
            print(f"Network monitor init failed: {e}")
            self.network_obj = SimpleNetworkMonitor()

        # Logs Viewer  
        try:
            if LogsViewer:
                # Use environment-appropriate log path
                log_path = self._get_log_path()
                self.logs_obj = LogsViewer(log_file=log_path)
            else:
                self.logs_obj = FallbackDisplay("Logs Viewer", CURRENT_ENV)
        except Exception as e:
            print(f"Logs viewer init failed: {e}")
            self.logs_obj = FallbackDisplay("Logs Viewer", CURRENT_ENV)

        # Process Monitor
        try:
            if ProcessMonitor:
                self.process_obj = ProcessMonitor()
            else:
                self.process_obj = SimpleProcessMonitor()
        except Exception as e:
            print(f"Process monitor init failed: {e}")
            self.process_obj = SimpleProcessMonitor()

        # Other panels with fallbacks
        self.sensors_obj = SensorsDashboard() if SensorsDashboard else FallbackDisplay("Sensors", CURRENT_ENV)
        self.decisions_obj = DecisionsView() if DecisionsView else FallbackDisplay("Decisions", CURRENT_ENV)
        self.anti_tamper_obj = AntiTamperControls() if AntiTamperControls else FallbackDisplay("Anti-Tamper", CURRENT_ENV)
        self.scripts_obj = ScriptsViewApp() if ScriptsViewApp else FallbackDisplay("Scripts", CURRENT_ENV)

    def _get_log_path(self):
        """Get appropriate log path for current environment."""
        base_logs = {
            "termux": "security/logs/events.log",
            "wsl2": "/var/log/blux/events.log", 
            "linux": "/var/log/blux/events.log",
            "macos": "/var/log/blux/events.log",
            "windows": "C:\\ProgramData\\BLUX\\logs\\events.log"
        }
        return base_logs.get(CURRENT_ENV, "security/logs/events.log")

    def compose(self) -> ComposeResult:
        """
        Compose the application layout.
        """
        # Use built-in Header/Footer if available, otherwise fallback
        try:
            yield Header()
        except Exception:
            yield Static(f"BLUX Guard Ultra Cockpit - {CURRENT_ENV}", id="app_header")
        
        container = Vertical(id="main_container")
        
        # Create all widgets
        self.network_widget = Static(self._generate_content(self.network_obj), id="network_panel")
        self.logs_widget = Static(self._generate_content(self.logs_obj), id="log_panel") 
        self.process_widget = Static(self._generate_content(self.process_obj), id="process_panel")
        self.sensors_widget = Static(self._generate_content(self.sensors_obj), id="sensors_panel")
        self.decisions_widget = Static(self._generate_content(self.decisions_obj), id="decisions_panel")
        self.anti_tamper_widget = Static(self._generate_content(self.anti_tamper_obj), id="controls_panel")
        self.scripts_widget = Static(self._generate_content(self.scripts_obj), id="scripts_panel")
        
        # Mount widgets
        yield container
        container.mount(
            self.network_widget,
            self.logs_widget, 
            self.process_widget,
            self.sensors_widget,
            self.decisions_widget,
            self.anti_tamper_widget,
            self.scripts_widget,
        )
        
        try:
            yield Footer()
        except Exception:
            yield Static("Ready - Press 'q' to quit, 'd' for dark mode", id="app_footer")

    def _generate_content(self, panel_obj: Any) -> str:
        """Safely generate content from panel object."""
        if panel_obj is None:
            return "[red]Not initialized[/red]"
            
        try:
            if hasattr(panel_obj, "generate_panel"):
                return panel_obj.generate_panel()
            elif hasattr(panel_obj, "generate_display"):
                return panel_obj.generate_display() 
            elif hasattr(panel_obj, "generate_table"):
                return panel_obj.generate_table()
            elif hasattr(panel_obj, "generate_decisions"):
                return panel_obj.generate_decisions()
            else:
                return str(panel_obj)
        except Exception as e:
            return f"[red]Error: {e}[/red]"

    def on_mount(self) -> None:
        """Start periodic refresh after mount."""
        self.set_interval(self.refresh_interval, self.update_panels)

    async def update_panels(self) -> None:
        """Refresh panel content safely."""
        widgets = [
            (self.network_widget, self.network_obj),
            (self.logs_widget, self.logs_obj),
            (self.process_widget, self.process_obj), 
            (self.sensors_widget, self.sensors_obj),
            (self.decisions_widget, self.decisions_obj),
            (self.anti_tamper_widget, self.anti_tamper_obj),
            (self.scripts_widget, self.scripts_obj)
        ]
        
        for widget, generator in widgets:
            if widget and generator:
                try:
                    new_content = self._generate_content(generator)
                    widget.update(new_content)
                except Exception as e:
                    widget.update(f"[red]Update error: {e}[/red]")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def main():
    """Main entry point with environment checks."""
    print(f"BLUX Guard Cockpit - Starting in {CURRENT_ENV} environment")
    print("Available modules:", {k: v for k, v in blux_modules.items() if v})
    
    if not TEXTUAL_AVAILABLE:
        print("ERROR: Textual framework is required but not available.")
        print("Install with: pip install textual")
        return 1
        
    try:
        app = DevMenuTreeApp()
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
