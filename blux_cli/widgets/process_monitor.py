#!/usr/bin/env python3
"""
BLUX Guard Process Monitor
Cross-platform process monitoring with security integration
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import time
import signal
import logging
import platform
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

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
    logger.warning("psutil not available - process monitoring will be limited")

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

class FallbackPrivilege:
    def get_privilege_info(self):
        is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        return {"is_root": is_root, "fallback": True, "platform": {"system": os.name, "architecture": platform.machine()}}


class ProcessAnalyzer:
    """
    Cross-platform process analysis with security context
    """
    
    def __init__(self):
        self.privilege_mgr = None
        self.current_user = self._get_current_user()
        
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception as e:
                logger.warning(f"Failed to initialize privilege manager: {e}")
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def _get_current_user(self) -> str:
        """Get current username in cross-platform way"""
        try:
            import getpass
            return getpass.getuser()
        except (ImportError, KeyError):
            return os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
    
    def get_process_list(self, max_processes: int = 20, show_all: bool = False) -> List[Dict[str, Any]]:
        """
        Get process list with security context
        """
        if not PSUTIL_AVAILABLE:
            return []
        
        processes = []
        try:
            # Determine which processes we can access based on privileges
            attrs = ['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'status', 'create_time']
            
            # Non-root users may not see all processes
            privilege_info = self.privilege_mgr.get_privilege_info()
            if not privilege_info['is_root'] and not show_all:
                # Only show user's processes in non-root mode
                for proc in psutil.process_iter(attrs):
                    try:
                        info = proc.info
                        if info.get('username') == self.current_user:
                            processes.append(self._enrich_process_info(info))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            else:
                # Root or show_all mode - try to get all processes
                for proc in psutil.process_iter(attrs):
                    try:
                        info = proc.info
                        processes.append(self._enrich_process_info(info))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Sort by CPU usage (most intensive first)
            processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)
            return processes[:max_processes]
            
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            return []
    
    def _enrich_process_info(self, proc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich process information with security context"""
        try:
            # Calculate memory usage
            mem_info = proc_info.get('memory_info')
            mem_mb = mem_info.rss / (1024 * 1024) if mem_info else 0
            
            # Determine security context
            username = proc_info.get('username', 'unknown')
            is_current_user = username == self.current_user
            is_system_process = username in ['root', 'SYSTEM', 'Administrator']
            
            # Security assessment
            security_level = "normal"
            if is_system_process and not self.privilege_mgr.is_root:
                security_level = "system"
            elif not is_current_user and not self.privilege_mgr.is_root:
                security_level = "other_user"
            
            return {
                "pid": proc_info.get('pid'),
                "name": proc_info.get('name', 'Unknown'),
                "cpu_percent": proc_info.get('cpu_percent', 0) or 0,
                "memory_mb": mem_mb,
                "username": username,
                "status": proc_info.get('status', 'unknown'),
                "create_time": proc_info.get('create_time'),
                "is_current_user": is_current_user,
                "is_system_process": is_system_process,
                "security_level": security_level
            }
        except Exception as e:
            logger.warning(f"Error enriching process info: {e}")
            return proc_info
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        if not PSUTIL_AVAILABLE:
            return {}
        
        try:
            # CPU statistics
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            # Memory statistics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Process statistics
            try:
                total_processes = len(psutil.pids())
            except:
                total_processes = 0
            
            # Load average (Unix-like systems)
            load_avg = self._get_load_average()
            
            # User process count
            user_processes = len([p for p in psutil.process_iter(['username']) 
                                if p.info.get('username') == self.current_user])
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_cores_logical": cpu_count_logical,
                "cpu_cores_physical": cpu_count_physical or cpu_count_logical,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used // (1024 * 1024),
                "memory_total_mb": memory.total // (1024 * 1024),
                "swap_percent": swap.percent,
                "total_processes": total_processes,
                "user_processes": user_processes,
                "load_avg": load_avg,
                "platform": PLATFORM
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    def _get_load_average(self) -> Tuple[float, float, float]:
        """Get load average in cross-platform way"""
        try:
            if hasattr(os, 'getloadavg'):
                return os.getloadavg()
            elif PSUTIL_AVAILABLE and hasattr(psutil, 'getloadavg'):
                return psutil.getloadavg()
            else:
                # Windows fallback - estimate from CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                load_estimate = cpu_percent / 100.0
                return (load_estimate, load_estimate, load_estimate)
        except (OSError, AttributeError):
            return (0.0, 0.0, 0.0)
    
    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific process"""
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            process = psutil.Process(pid)
            with process.oneshot():
                info = {
                    "pid": pid,
                    "name": process.name(),
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "memory_rss_mb": process.memory_info().rss / (1024 * 1024),
                    "username": process.username(),
                    "create_time": process.create_time(),
                    "exe": process.exe(),
                    "cmdline": process.cmdline(),
                    "cwd": process.cwd(),
                    "num_threads": process.num_threads(),
                    "nice": process.nice() if hasattr(process, 'nice') else None,
                    "io_counters": self._get_io_counters(process),
                    "connections": self._get_network_connections(process)
                }
            return info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def _get_io_counters(self, process) -> Optional[Dict[str, Any]]:
        """Get IO counters if available"""
        try:
            io = process.io_counters()
            return {
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
                "read_count": io.read_count,
                "write_count": io.write_count
            }
        except (psutil.AccessDenied, AttributeError):
            return None
    
    def _get_network_connections(self, process) -> List[Dict[str, Any]]:
        """Get network connections if available"""
        try:
            connections = process.connections()
            return [
                {
                    "family": conn.family.name,
                    "type": conn.type.name,
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status
                }
                for conn in connections[:5]  # Limit to first 5 connections
            ]
        except (psutil.AccessDenied, AttributeError):
            return []


class ProcessMonitor:
    """
    Enhanced Process Monitor with security integration
    """
    
    def __init__(self, refresh_interval: float = 2.0, max_processes: int = 20):
        self.refresh_interval = refresh_interval
        self.max_processes = max_processes
        self.analyzer = ProcessAnalyzer()
        self.running = True
        
        # Signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Process Monitor initialized for platform: {PLATFORM}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if RICH_AVAILABLE:
            console.print("\n[yellow]🛑 Shutting down Process Monitor...[/yellow]")
        else:
            print("\n🛑 Shutting down Process Monitor...")
        self.running = False
    
    def _format_memory(self, mb: float) -> str:
        """Format memory usage for display"""
        if mb >= 1024:
            return f"{mb/1024:.1f} GB"
        else:
            return f"{mb:.1f} MB"
    
    def _get_cpu_style(self, cpu_percent: float) -> str:
        """Get color style for CPU usage"""
        if cpu_percent > 70:
            return "bold red"
        elif cpu_percent > 30:
            return "yellow"
        else:
            return "green"
    
    def _get_memory_style(self, memory_mb: float) -> str:
        """Get color style for memory usage"""
        if memory_mb > 1000:
            return "bold red"
        elif memory_mb > 500:
            return "yellow"
        else:
            return "green"
    
    def _get_status_style(self, status: str) -> str:
        """Get color style for process status"""
        status_map = {
            'running': 'green',
            'sleeping': 'blue',
            'idle': 'cyan',
            'zombie': 'red',
            'stopped': 'yellow'
        }
        return status_map.get(status.lower(), 'white')
    
    def _get_security_indicator(self, process_info: Dict[str, Any]) -> str:
        """Get security indicator for process"""
        if process_info.get('is_system_process'):
            return "🔴"  # System process
        elif not process_info.get('is_current_user'):
            return "🟡"  # Other user's process
        else:
            return "🟢"  # Current user's process
    
    def generate_rich_dashboard(self) -> Panel:
        """Generate rich formatted process dashboard"""
        processes = self.analyzer.get_process_list(self.max_processes)
        system_stats = self.analyzer.get_system_stats()
        
        # Create main layout
        layout = Layout()
        
        # Header with system info
        header_text = Text()
        header_text.append("🔍 BLUX Guard Process Monitor", style="bold cyan")
        header_text.append(f" • {PLATFORM.upper()}", style="bold magenta")
        if self.analyzer.privilege_mgr:
            privilege_info = self.analyzer.privilege_mgr.get_privilege_info()
            header_text.append(f" • {privilege_info['privilege_level'].upper()}", 
                             style="bold red" if privilege_info['is_root'] else "bold green")
        
        header_panel = Panel(header_text, box=box.ROUNDED, style="bold blue")
        
        # System statistics panel
        if system_stats:
            stats_content = f"""
CPU: {system_stats['cpu_percent']:.1f}% ({system_stats['cpu_cores_physical']}P/{system_stats['cpu_cores_logical']}L)
Memory: {system_stats['memory_percent']:.1f}% ({system_stats['memory_used_mb']}MB/{system_stats['memory_total_mb']}MB)
Processes: {system_stats['total_processes']} total, {system_stats['user_processes']} user
Load: {system_stats['load_avg'][0]:.2f}, {system_stats['load_avg'][1]:.2f}, {system_stats['load_avg'][2]:.2f}
"""
            stats_panel = Panel(stats_content, title="📊 System Statistics", box=box.SIMPLE)
        else:
            stats_panel = Panel("[red]System statistics unavailable[/red]", title="📊 System Statistics")
        
        # Processes table
        table = Table(title=f"📋 Top {len(processes)} Processes", box=box.ROUNDED, show_header=True)
        table.add_column("Sec", style="white", width=3)
        table.add_column("PID", style="cyan", width=8)
        table.add_column("Name", style="magenta", min_width=15)
        table.add_column("User", style="blue", min_width=10)
        table.add_column("CPU%", justify="right", style="green", width=8)
        table.add_column("Memory", justify="right", style="yellow", width=12)
        table.add_column("Status", justify="center", style="red", width=10)
        
        if not processes:
            table.add_row("", "No", "processes", "found", "N/A", "N/A", "N/A")
        else:
            for proc in processes:
                security_indicator = self._get_security_indicator(proc)
                cpu_style = self._get_cpu_style(proc['cpu_percent'])
                mem_style = self._get_memory_style(proc['memory_mb'])
                status_style = self._get_status_style(proc['status'])
                
                table.add_row(
                    security_indicator,
                    str(proc['pid']),
                    proc['name'][:20],
                    proc['username'][:8],
                    Text(f"{proc['cpu_percent']:.1f}", style=cpu_style),
                    Text(self._format_memory(proc['memory_mb']), style=mem_style),
                    Text(proc['status'][:8], style=status_style)
                )
        
        # Security context panel
        if self.analyzer.privilege_mgr:
            privilege_info = self.analyzer.privilege_mgr.get_privilege_info()
            security_text = Text()
            security_text.append("🔒 Security Context:\n", style="bold")
            security_text.append(f"Mode: {'ROOT' if privilege_info['is_root'] else 'USER'}\n")
            security_text.append(f"User: {self.analyzer.current_user}\n")
            
            if not privilege_info['is_root']:
                security_text.append("\n⚠️  Limited to user processes only", style="yellow")
                security_text.append("\n🟢 Your processes  🟡 Other users  🔴 System", style="dim")
            
            security_panel = Panel(security_text, box=box.SIMPLE, style="dim")
            
            # Final layout with security
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(stats_panel, size=5),
                Layout(table, size=12),
                Layout(security_panel, size=4)
            )
        else:
            # Layout without security context
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(stats_panel, size=5),
                Layout(table, size=16)
            )
        
        return Panel(layout, title="BLUX Guard Security Monitoring", box=box.DOUBLE_EDGE)
    
    def generate_basic_dashboard(self) -> str:
        """Generate basic console dashboard for environments without rich"""
        processes = self.analyzer.get_process_list(self.max_processes)
        system_stats = self.analyzer.get_system_stats()
        
        output = []
        output.append("=" * 70)
        output.append("              BLUX Guard Process Monitor")
        output.append(f"         Platform: {PLATFORM} • User: {self.analyzer.current_user}")
        output.append("=" * 70)
        
        # System statistics
        if system_stats:
            output.append(f"CPU: {system_stats['cpu_percent']:.1f}% | Memory: {system_stats['memory_percent']:.1f}%")
            output.append(f"Processes: {system_stats['total_processes']} total, {system_stats['user_processes']} user")
            output.append(f"Load: {system_stats['load_avg'][0]:.2f}, {system_stats['load_avg'][1]:.2f}, {system_stats['load_avg'][2]:.2f}")
        output.append("-" * 70)
        
        # Process table header
        output.append(f"{'Sec':<3} {'PID':<8} {'Name':<20} {'User':<10} {'CPU%':<6} {'Memory':<12} {'Status':<10}")
        output.append("-" * 70)
        
        if not processes:
            output.append("No processes found")
        else:
            for proc in processes:
                security_indicator = self._get_security_indicator(proc)
                output.append(f"{security_indicator:<3} {proc['pid']:<8} {proc['name'][:19]:<20} "
                            f"{proc['username'][:9]:<10} {proc['cpu_percent']:5.1f} "
                            f"{self._format_memory(proc['memory_mb']):<12} {proc['status'][:9]:<10}")
        
        output.append("=" * 70)
        output.append("Legend: 🟢 Your process  🟡 Other user  🔴 System process")
        output.append("Press Ctrl+C to exit")
        
        return "\n".join(output)
    
    def run(self):
        """Run the process monitor"""
        if not PSUTIL_AVAILABLE:
            console.print("[red]❌ psutil not available - process monitor cannot run[/red]")
            console.print("[yellow]💡 Install with: pip install psutil[/yellow]")
            return
        
        try:
            if RICH_AVAILABLE:
                with Live(console=console, screen=True, refresh_per_second=1/self.refresh_interval) as live:
                    while self.running:
                        dashboard = self.generate_rich_dashboard()
                        live.update(dashboard)
                        time.sleep(self.refresh_interval)
            else:
                while self.running:
                    os.system('cls' if PLATFORM == 'windows' else 'clear')
                    dashboard = self.generate_basic_dashboard()
                    print(dashboard)
                    time.sleep(self.refresh_interval)
                    
        except KeyboardInterrupt:
            self._signal_handler(None, None)
        except Exception as e:
            logger.error(f"Process monitor error: {e}")
            console.print(f"[red]❌ Monitor error: {e}[/red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BLUX Guard Process Monitor")
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=2.0,
        help="Refresh interval in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=20,
        help="Maximum number of processes to display (default: 20)"
    )
    parser.add_argument(
        "--basic", "-b",
        action="store_true",
        help="Force basic console mode"
    )
    
    args = parser.parse_args()
    
    try:
        monitor = ProcessMonitor(refresh_interval=args.interval, max_processes=args.max)
        monitor.run()
    except KeyboardInterrupt:
        print("\n👋 Process Monitor stopped by user")
    except Exception as e:
        logger.error(f"Failed to start process monitor: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
