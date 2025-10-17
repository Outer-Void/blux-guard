#!/usr/bin/env python3
"""
BLUX Guard Sensors Dashboard
Cross-platform system monitoring with security integration
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import signal
import platform
import logging
from pathlib import Path
from time import sleep
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - sensor data will be limited")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.warning("Rich not available - using basic console")

# Security integration
try:
    from blux_modules.security.privilege_manager import PrivilegeManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Platform detection
def detect_platform() -> str:
    """Detect current platform with enhanced detection"""
    system = platform.system().lower()
    
    if hasattr(os, 'getppid') and 'termux' in os.environ.get('PREFIX', '').lower():
        return "termux"
    elif os.path.exists('/system/bin/adb') or os.path.exists('/system/app'):
        return "android"
    elif 'microsoft' in platform.release().lower() or 'wsl' in platform.release().lower():
        return "wsl2"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

PLATFORM = detect_platform()

class FallbackPrivilege:
    def get_privilege_info(self):
        is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        return {"is_root": is_root, "fallback": True, "platform": {"system": os.name, "architecture": platform.machine()}}

# Fallback console if rich is not available
if not RICH_AVAILABLE:
    class BasicConsole:
        def print(self, *args, **kwargs):
            print(*args)
        
        def rule(self, title):
            print(f"\n{'='*60}")
            print(f" {title}")
            print(f"{'='*60}")
    
    console = BasicConsole()
else:
    console = Console()


class SystemSensors:
    """
    Cross-platform system sensor data collection
    With privilege-aware fallbacks for non-root environments
    """
    
    def __init__(self):
        self.privilege_mgr = None
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception as e:
                logger.warning(f"Failed to initialize privilege manager: {e}")
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information with fallbacks"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            
            return {
                "usage_percent": cpu_percent,
                "cores_logical": cpu_count_logical,
                "cores_physical": cpu_count_physical or cpu_count_logical,
                "frequency_current": getattr(cpu_freq, 'current', None),
                "frequency_max": getattr(cpu_freq, 'max', None),
                "status": "normal"
            }
        except Exception as e:
            logger.error(f"CPU info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_mb": mem.total // (1024 * 1024),
                "used_mb": mem.used // (1024 * 1024),
                "available_mb": mem.available // (1024 * 1024),
                "usage_percent": mem.percent,
                "swap_total_mb": swap.total // (1024 * 1024),
                "swap_used_mb": swap.used // (1024 * 1024),
                "swap_percent": swap.percent,
                "status": "normal"
            }
        except Exception as e:
            logger.error(f"Memory info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information with platform-specific paths"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            # Platform-specific mount points
            if PLATFORM in ["android", "termux"]:
                mount_points = ["/", "/data", "/storage"]
            elif PLATFORM == "windows":
                mount_points = ["C:\\"]
            elif PLATFORM == "macos":
                mount_points = ["/", "/System/Volumes/Data"]
            else:  # linux, wsl2
                mount_points = ["/", "/home"]
            
            disk_info = {}
            for mount in mount_points:
                try:
                    usage = psutil.disk_usage(mount)
                    disk_info[mount] = {
                        "total_gb": usage.total // (1024**3),
                        "used_gb": usage.used // (1024**3),
                        "free_gb": usage.free // (1024**3),
                        "usage_percent": usage.percent
                    }
                except (PermissionError, FileNotFoundError):
                    continue
            
            return {
                "partitions": disk_info,
                "status": "normal"
            }
        except Exception as e:
            logger.error(f"Disk info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information with privilege awareness"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            net_io = psutil.net_io_counters()
            net_connections = []
            
            # Only collect connections if we have privileges
            privilege_info = self.privilege_mgr.get_privilege_info()
            if privilege_info and privilege_info['is_root']:
                try:
                    net_connections = list(psutil.net_connections(kind='inet')[:10])  # Limit for performance
                except (psutil.AccessDenied, PermissionError):
                    logger.debug("Insufficient privileges for network connections")
            
            return {
                "bytes_sent": getattr(net_io, 'bytes_sent', 0),
                "bytes_recv": getattr(net_io, 'bytes_recv', 0),
                "packets_sent": getattr(net_io, 'packets_sent', 0),
                "packets_recv": getattr(net_io, 'packets_recv', 0),
                "active_connections": len(net_connections),
                "status": "normal"
            }
        except Exception as e:
            logger.error(f"Network info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get process information with privilege awareness"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            # Get process count
            processes = list(psutil.process_iter(['pid', 'name', 'username']))
            process_count = len(processes)
            
            # Get current user processes
            current_user = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
            user_processes = [p for p in processes if getattr(p.info, 'username', None) == current_user]
            
            return {
                "total_processes": process_count,
                "user_processes": len(user_processes),
                "status": "normal"
            }
        except Exception as e:
            logger.error(f"Process info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information if available"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "time_left": getattr(battery, 'secsleft', None),
                    "status": "normal"
                }
            else:
                return {"status": "unavailable", "message": "No battery detected"}
        except Exception as e:
            logger.error(f"Battery info error: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        privilege_info = self.privilege_mgr.get_privilege_info()
        return {
            "platform": PLATFORM,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "privilege_level": "root" if (privilege_info and privilege_info['is_root']) else "user"
        }
    
    def get_all_sensors(self) -> Dict[str, Any]:
        """Get all sensor data"""
        return {
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "processes": self.get_process_info(),
            "battery": self.get_battery_info(),
            "timestamp": platform.python_implementation()  # Simple timestamp alternative
        }


class SensorsDashboard:
    """
    Enhanced Sensors Dashboard with security integration
    Cross-platform compatible with rich fallbacks
    """
    
    def __init__(self, refresh_interval: float = 2.0):
        self.refresh_interval = refresh_interval
        self.running = True
        self.sensors = SystemSensors()
        
        # Signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Sensors Dashboard initialized for platform: {PLATFORM}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if RICH_AVAILABLE:
            console.print("\n[yellow]🛑 Shutting down Sensors Dashboard...[/yellow]")
        else:
            print("\n🛑 Shutting down Sensors Dashboard...")
        self.running = False
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status indicator"""
        status_colors = {
            "normal": "green",
            "warning": "yellow", 
            "error": "red",
            "unavailable": "blue"
        }
        return status_colors.get(status, "white")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def generate_rich_dashboard(self) -> Panel:
        """Generate rich formatted dashboard"""
        sensor_data = self.sensors.get_all_sensors()
        
        # Create main layout
        layout = Layout()
        
        # Header with system info
        system_info = sensor_data["system"]
        header_text = Text()
        header_text.append("🔍 BLUX Guard Sensors Dashboard", style="bold cyan")
        header_text.append(f" • {system_info['platform'].upper()}", style="bold magenta")
        header_text.append(f" • {system_info['privilege_level'].upper()}", 
                          style="bold red" if system_info['privilege_level'] == 'root' else "bold green")
        
        header_panel = Panel(header_text, box=box.ROUNDED, style="bold blue")
        
        # Create columns for sensor data
        columns_layout = Layout()
        columns_layout.split_row(
            Layout(name="left", size=40),
            Layout(name="right", size=40)
        )
        
        # Left column - System & CPU
        left_table = Table(title="🖥️ System & CPU", box=box.ROUNDED, show_header=False)
        left_table.add_column("Metric", style="cyan", no_wrap=True)
        left_table.add_column("Value", style="white")
        
        # System info
        left_table.add_row("Platform", f"{system_info['system']} {system_info['release']}")
        left_table.add_row("Architecture", system_info['architecture'])
        left_table.add_row("Python", system_info['python_version'])
        
        # CPU info
        cpu_info = sensor_data["cpu"]
        if "error" not in cpu_info:
            left_table.add_row("CPU Usage", f"{cpu_info['usage_percent']:.1f}%")
            left_table.add_row("Cores", f"{cpu_info['cores_physical']}P + {cpu_info['cores_logical'] - cpu_info['cores_physical']}L")
            if cpu_info.get('frequency_current'):
                left_table.add_row("Frequency", f"{cpu_info['frequency_current']:.0f} MHz")
        else:
            left_table.add_row("CPU", f"[red]Error: {cpu_info['error']}[/red]")
        
        # Memory info
        mem_info = sensor_data["memory"]
        if "error" not in mem_info:
            left_table.add_row("Memory", f"{mem_info['usage_percent']:.1f}%")
            left_table.add_row("RAM Used", f"{mem_info['used_mb']} MB")
            left_table.add_row("Swap", f"{mem_info.get('swap_percent', 0):.1f}%")
        else:
            left_table.add_row("Memory", f"[red]Error: {mem_info['error']}[/red]")
        
        # Right column - Storage & Network
        right_table = Table(title="💾 Storage & Network", box=box.ROUNDED, show_header=False)
        right_table.add_column("Metric", style="cyan", no_wrap=True)
        right_table.add_column("Value", style="white")
        
        # Disk info
        disk_info = sensor_data["disk"]
        if "error" not in disk_info and "partitions" in disk_info:
            for mount, info in list(disk_info["partitions"].items())[:2]:  # Show first 2 partitions
                mount_name = mount.replace('\\', '').replace('/', '') or 'Root'
                right_table.add_row(f"Disk {mount_name}", f"{info['usage_percent']:.1f}%")
        else:
            right_table.add_row("Disk", f"[red]Error: {disk_info.get('error', 'Unknown')}[/red]")
        
        # Network info
        net_info = sensor_data["network"]
        if "error" not in net_info:
            right_table.add_row("Net Up", self._format_bytes(net_info['bytes_sent']))
            right_table.add_row("Net Down", self._format_bytes(net_info['bytes_recv']))
            right_table.add_row("Connections", f"{net_info['active_connections']}")
        else:
            right_table.add_row("Network", f"[red]Error: {net_info['error']}[/red]")
        
        # Processes
        proc_info = sensor_data["processes"]
        if "error" not in proc_info:
            right_table.add_row("Processes", f"{proc_info['total_processes']} total")
            right_table.add_row("User Procs", f"{proc_info['user_processes']}")
        else:
            right_table.add_row("Processes", f"[red]Error: {proc_info['error']}[/red]")
        
        # Battery
        battery_info = sensor_data["battery"]
        if "error" not in battery_info and battery_info.get("status") != "unavailable":
            battery_icon = "🔌" if battery_info['power_plugged'] else "🔋"
            right_table.add_row("Battery", f"{battery_icon} {battery_info['percent']:.0f}%")
        
        # Assemble columns
        columns_layout["left"].update(left_table)
        columns_layout["right"].update(right_table)
        
        # Security status
        if self.sensors.privilege_mgr:
            privilege_info = self.sensors.privilege_mgr.get_privilege_info()
            security_text = Text()
            security_text.append("🔒 Security Status: ", style="bold")
            security_text.append(
                "ROOT" if privilege_info['is_root'] else "USER", 
                style="bold red" if privilege_info['is_root'] else "bold green"
            )
            
            if not privilege_info['is_root']:
                security_text.append("\n⚠️  Some sensors limited in user mode", style="yellow")
            
            security_panel = Panel(security_text, box=box.SIMPLE, style="dim")
            
            # Final layout
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(columns_layout, size=12),
                Layout(security_panel, size=3)
            )
        else:
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(columns_layout, size=15)
            )
        
        return Panel(layout, title="BLUX Guard Security Monitoring", box=box.DOUBLE_EDGE)
    
    def generate_basic_dashboard(self) -> str:
        """Generate basic console dashboard for environments without rich"""
        sensor_data = self.sensors.get_all_sensors()
        system_info = sensor_data["system"]
        
        output = []
        output.append("=" * 60)
        output.append("           BLUX Guard Sensors Dashboard")
        output.append(f"      Platform: {system_info['platform']} • Mode: {system_info['privilege_level']}")
        output.append("=" * 60)
        
        # CPU
        cpu_info = sensor_data["cpu"]
        if "error" not in cpu_info:
            output.append(f"CPU: {cpu_info['usage_percent']:.1f}% | Cores: {cpu_info['cores_logical']}")
        else:
            output.append(f"CPU: ERROR - {cpu_info['error']}")
        
        # Memory
        mem_info = sensor_data["memory"]
        if "error" not in mem_info:
            output.append(f"RAM: {mem_info['usage_percent']:.1f}% | Used: {mem_info['used_mb']}MB")
        else:
            output.append(f"RAM: ERROR - {mem_info['error']}")
        
        # Disk
        disk_info = sensor_data["disk"]
        if "error" not in disk_info and "partitions" in disk_info:
            for mount, info in disk_info["partitions"].items():
                mount_name = mount.replace('\\', '').replace('/', '') or 'Root'
                output.append(f"Disk {mount_name}: {info['usage_percent']:.1f}%")
        
        # Network
        net_info = sensor_data["network"]
        if "error" not in net_info:
            output.append(f"Network: ↑{self._format_bytes(net_info['bytes_sent'])} ↓{self._format_bytes(net_info['bytes_recv'])}")
        
        # Security note
        privilege_info = self.sensors.privilege_mgr.get_privilege_info()
        if self.sensors.privilege_mgr and not privilege_info['is_root']:
            output.append("NOTE: Running in user mode - some sensors limited")
        
        output.append("=" * 60)
        output.append("Press Ctrl+C to exit")
        
        return "\n".join(output)
    
    def run(self):
        """Run the sensors dashboard"""
        if not PSUTIL_AVAILABLE:
            console.print("[red]❌ psutil not available - sensors dashboard cannot run[/red]")
            console.print("[yellow]💡 Install with: pip install psutil[/yellow]")
            return
        
        try:
            if RICH_AVAILABLE:
                with Live(console=console, screen=True, refresh_per_second=1/self.refresh_interval) as live:
                    while self.running:
                        dashboard = self.generate_rich_dashboard()
                        live.update(dashboard)
                        sleep(self.refresh_interval)
            else:
                while self.running:
                    os.system('cls' if PLATFORM == 'windows' else 'clear')
                    dashboard = self.generate_basic_dashboard()
                    print(dashboard)
                    sleep(self.refresh_interval)
                    
        except KeyboardInterrupt:
            self._signal_handler(None, None)
        except Exception as e:
            logger.error(f"Sensors dashboard error: {e}")
            console.print(f"[red]❌ Dashboard error: {e}[/red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BLUX Guard Sensors Dashboard")
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=2.0,
        help="Refresh interval in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--basic", "-b",
        action="store_true",
        help="Force basic console mode"
    )
    
    args = parser.parse_args()
    
    try:
        dashboard = SensorsDashboard(refresh_interval=args.interval)
        dashboard.run()
    except KeyboardInterrupt:
        print("\n👋 Sensors Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Failed to start sensors dashboard: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
