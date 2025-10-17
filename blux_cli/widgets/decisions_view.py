#!/usr/bin/env python3
"""
BLUX Guard Decisions Engine
Cross-platform security decision making with system monitoring
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
from datetime import datetime, timedelta

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
    logger.warning("psutil not available - system monitoring will be limited")

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


class SecurityDecisions:
    """
    Cross-platform security decision engine
    """
    
    def __init__(self):
        self.privilege_mgr = None
        self.decision_history = []
        self.alert_thresholds = self._get_default_thresholds()
        
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception as e:
                logger.warning(f"Failed to initialize privilege manager: {e}")
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """Get default security thresholds"""
        return {
            "cpu_critical": 90.0,
            "cpu_warning": 80.0,
            "memory_critical": 90.0,
            "memory_warning": 80.0,
            "disk_critical": 95.0,
            "disk_warning": 85.0,
            "swap_critical": 80.0,
            "swap_warning": 60.0,
            "process_limit": 200,
            "connection_limit": 100,
            "uptime_warning_days": 30
        }
    
    def analyze_system_security(self) -> List[Dict[str, Any]]:
        """
        Analyze system security and generate decisions
        """
        decisions = []
        
        if not PSUTIL_AVAILABLE:
            decisions.append({
                "category": "System",
                "decision": "System Monitoring Unavailable",
                "recommendation": "Install psutil for system monitoring",
                "severity": "warning",
                "metric": "N/A",
                "timestamp": datetime.now()
            })
            return decisions
        
        try:
            # CPU Analysis
            cpu_decisions = self._analyze_cpu_security()
            decisions.extend(cpu_decisions)
            
            # Memory Analysis
            memory_decisions = self._analyze_memory_security()
            decisions.extend(memory_decisions)
            
            # Disk Analysis
            disk_decisions = self._analyze_disk_security()
            decisions.extend(disk_decisions)
            
            # Process Analysis
            process_decisions = self._analyze_process_security()
            decisions.extend(process_decisions)
            
            # Network Analysis
            network_decisions = self._analyze_network_security()
            decisions.extend(network_decisions)
            
            # System Health Analysis
            system_decisions = self._analyze_system_health()
            decisions.extend(system_decisions)
            
            # Security Context Analysis
            security_decisions = self._analyze_security_context()
            decisions.extend(security_decisions)
            
            # Update decision history
            self.decision_history.extend(decisions)
            if len(self.decision_history) > 100:  # Keep last 100 decisions
                self.decision_history = self.decision_history[-100:]
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
            decisions.append({
                "category": "System",
                "decision": "Analysis Error",
                "recommendation": f"Check system monitoring: {e}",
                "severity": "error",
                "metric": "N/A",
                "timestamp": datetime.now()
            })
            return decisions
    
    def _analyze_cpu_security(self) -> List[Dict[str, Any]]:
        """Analyze CPU usage for security decisions"""
        decisions = []
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            load_avg = self._get_load_average()
            
            if cpu_percent > self.alert_thresholds["cpu_critical"]:
                decisions.append({
                    "category": "CPU",
                    "decision": "Critical CPU Load",
                    "recommendation": "Investigate resource-intensive processes immediately",
                    "severity": "critical",
                    "metric": f"{cpu_percent:.1f}%",
                    "timestamp": datetime.now()
                })
            elif cpu_percent > self.alert_thresholds["cpu_warning"]:
                decisions.append({
                    "category": "CPU",
                    "decision": "High CPU Load",
                    "recommendation": "Monitor system performance and consider optimization",
                    "severity": "warning",
                    "metric": f"{cpu_percent:.1f}%",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "CPU",
                    "decision": "CPU Load Normal",
                    "recommendation": "System operating within normal parameters",
                    "severity": "normal",
                    "metric": f"{cpu_percent:.1f}%",
                    "timestamp": datetime.now()
                })
            
            # Load average analysis
            if load_avg[0] > psutil.cpu_count() * 2:
                decisions.append({
                    "category": "CPU",
                    "decision": "High System Load",
                    "recommendation": "System under heavy load, consider reducing workload",
                    "severity": "warning",
                    "metric": f"{load_avg[0]:.2f}",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"CPU analysis error: {e}")
        
        return decisions
    
    def _analyze_memory_security(self) -> List[Dict[str, Any]]:
        """Analyze memory usage for security decisions"""
        decisions = []
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # RAM analysis
            if memory.percent > self.alert_thresholds["memory_critical"]:
                decisions.append({
                    "category": "Memory",
                    "decision": "Critical Memory Usage",
                    "recommendation": "Free up memory immediately to prevent system instability",
                    "severity": "critical",
                    "metric": f"{memory.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            elif memory.percent > self.alert_thresholds["memory_warning"]:
                decisions.append({
                    "category": "Memory",
                    "decision": "High Memory Usage",
                    "recommendation": "Consider closing unused applications",
                    "severity": "warning",
                    "metric": f"{memory.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "Memory",
                    "decision": "Memory Usage Normal",
                    "recommendation": "Adequate memory available",
                    "severity": "normal",
                    "metric": f"{memory.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            
            # Swap analysis
            if swap.percent > self.alert_thresholds["swap_critical"]:
                decisions.append({
                    "category": "Memory",
                    "decision": "Critical Swap Usage",
                    "recommendation": "System relying heavily on swap, add more RAM",
                    "severity": "critical",
                    "metric": f"{swap.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            elif swap.percent > self.alert_thresholds["swap_warning"]:
                decisions.append({
                    "category": "Memory",
                    "decision": "High Swap Usage",
                    "recommendation": "Monitor swap usage and consider RAM upgrade",
                    "severity": "warning",
                    "metric": f"{swap.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Memory analysis error: {e}")
        
        return decisions
    
    def _analyze_disk_security(self) -> List[Dict[str, Any]]:
        """Analyze disk usage for security decisions"""
        decisions = []
        
        try:
            # Check root filesystem
            disk = psutil.disk_usage("/")
            
            if disk.percent > self.alert_thresholds["disk_critical"]:
                decisions.append({
                    "category": "Storage",
                    "decision": "Critical Disk Usage",
                    "recommendation": "Free up disk space immediately",
                    "severity": "critical",
                    "metric": f"{disk.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            elif disk.percent > self.alert_thresholds["disk_warning"]:
                decisions.append({
                    "category": "Storage",
                    "decision": "High Disk Usage",
                    "recommendation": "Consider cleaning up unnecessary files",
                    "severity": "warning",
                    "metric": f"{disk.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "Storage",
                    "decision": "Disk Usage Normal",
                    "recommendation": "Adequate disk space available",
                    "severity": "normal",
                    "metric": f"{disk.percent:.1f}%",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Disk analysis error: {e}")
        
        return decisions
    
    def _analyze_process_security(self) -> List[Dict[str, Any]]:
        """Analyze process security"""
        decisions = []
        
        try:
            process_count = len(psutil.pids())
            
            if process_count > self.alert_thresholds["process_limit"]:
                decisions.append({
                    "category": "Processes",
                    "decision": "High Process Count",
                    "recommendation": "Monitor for potential fork bombs or resource abuse",
                    "severity": "warning",
                    "metric": f"{process_count} processes",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "Processes",
                    "decision": "Process Count Normal",
                    "recommendation": "System process count within expected range",
                    "severity": "normal",
                    "metric": f"{process_count} processes",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Process analysis error: {e}")
        
        return decisions
    
    def _analyze_network_security(self) -> List[Dict[str, Any]]:
        """Analyze network security"""
        decisions = []
        
        try:
            # Network connections
            privilege_info = self.privilege_mgr.get_privilege_info()
            if privilege_info and privilege_info['is_root']:
                connections = len(psutil.net_connections())
                
                if connections > self.alert_thresholds["connection_limit"]:
                    decisions.append({
                        "category": "Network",
                        "decision": "High Network Activity",
                        "recommendation": "Review network connections for suspicious activity",
                        "severity": "warning",
                        "metric": f"{connections} connections",
                        "timestamp": datetime.now()
                    })
                else:
                    decisions.append({
                        "category": "Network",
                        "decision": "Network Activity Normal",
                        "recommendation": "Network connections within expected range",
                        "severity": "normal",
                        "metric": f"{connections} connections",
                        "timestamp": datetime.now()
                    })
            else:
                decisions.append({
                    "category": "Network",
                    "decision": "Limited Network Visibility",
                    "recommendation": "Run with root privileges for full network monitoring",
                    "severity": "info",
                    "metric": "Limited access",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Network analysis error: {e}")
        
        return decisions
    
    def _analyze_system_health(self) -> List[Dict[str, Any]]:
        """Analyze overall system health"""
        decisions = []
        
        try:
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_days = uptime_seconds / (24 * 3600)
            
            if uptime_days > self.alert_thresholds["uptime_warning_days"]:
                decisions.append({
                    "category": "System",
                    "decision": "Long System Uptime",
                    "recommendation": "Consider scheduled reboot for system maintenance",
                    "severity": "info",
                    "metric": f"{uptime_days:.1f} days",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "System",
                    "decision": "System Uptime Normal",
                    "recommendation": "System recently maintained",
                    "severity": "normal",
                    "metric": f"{uptime_days:.1f} days",
                    "timestamp": datetime.now()
                })
            
            # Battery health (if available)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    if battery.percent < 20 and not battery.power_plugged:
                        decisions.append({
                            "category": "Power",
                            "decision": "Low Battery",
                            "recommendation": "Connect to power source soon",
                            "severity": "warning",
                            "metric": f"{battery.percent}%",
                            "timestamp": datetime.now()
                        })
            except AttributeError:
                pass  # Battery not available on this system
            
        except Exception as e:
            logger.error(f"System health analysis error: {e}")
        
        return decisions
    
    def _analyze_security_context(self) -> List[Dict[str, Any]]:
        """Analyze security context and privileges"""
        decisions = []
        
        if not self.privilege_mgr:
            decisions.append({
                "category": "Security",
                "decision": "Security System Unavailable",
                "recommendation": "Security modules not loaded",
                "severity": "warning",
                "metric": "N/A",
                "timestamp": datetime.now()
            })
            return decisions
        
        try:
            priv_info = self.privilege_mgr.get_privilege_info()
            
            if priv_info['is_root']:
                decisions.append({
                    "category": "Security",
                    "decision": "Running with Root Privileges",
                    "recommendation": "Exercise caution - full system access enabled",
                    "severity": "warning",
                    "metric": "ROOT",
                    "timestamp": datetime.now()
                })
            else:
                decisions.append({
                    "category": "Security",
                    "decision": "Running in User Mode",
                    "recommendation": "Some security features limited",
                    "severity": "info",
                    "metric": "USER",
                    "timestamp": datetime.now()
                })
            
            # Platform-specific security considerations
            if PLATFORM in ["android", "termux"]:
                decisions.append({
                    "category": "Security",
                    "decision": "Mobile Environment",
                    "recommendation": "Some system monitoring features may be limited",
                    "severity": "info",
                    "metric": PLATFORM.upper(),
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Security context analysis error: {e}")
        
        return decisions
    
    def _get_load_average(self) -> Tuple[float, float, float]:
        """Get load average in cross-platform way"""
        try:
            if hasattr(os, 'getloadavg'):
                return os.getloadavg()
            elif PSUTIL_AVAILABLE and hasattr(psutil, 'getloadavg'):
                return psutil.getloadavg()
            else:
                return (0.0, 0.0, 0.0)
        except (OSError, AttributeError):
            return (0.0, 0.0, 0.0)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics"""
        decisions = self.analyze_system_security()
        
        severity_counts = {
            "critical": 0,
            "warning": 0,
            "normal": 0,
            "info": 0,
            "error": 0
        }
        
        for decision in decisions:
            severity_counts[decision["severity"]] += 1
        
        return {
            "total_decisions": len(decisions),
            "severity_counts": severity_counts,
            "timestamp": datetime.now(),
            "platform": PLATFORM
        }


class DecisionsView:
    """
    Enhanced Decisions Engine with security integration
    """
    
    def __init__(self, refresh_interval: float = 2.0):
        self.refresh_interval = refresh_interval
        self.decisions_engine = SecurityDecisions()
        self.running = True
        
        # Signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Decisions View initialized for platform: {PLATFORM}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if RICH_AVAILABLE:
            console.print("\n[yellow]🛑 Shutting down Decisions Engine...[/yellow]")
        else:
            print("\n🛑 Shutting down Decisions Engine...")
        self.running = False
    
    def _get_severity_style(self, severity: str) -> str:
        """Get color style for decision severity"""
        severity_styles = {
            "critical": "bold red",
            "warning": "yellow",
            "normal": "green",
            "info": "blue",
            "error": "red"
        }
        return severity_styles.get(severity, "white")
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for decision category"""
        category_icons = {
            "CPU": "🖥️",
            "Memory": "💾",
            "Storage": "💽",
            "Processes": "⚙️",
            "Network": "🌐",
            "System": "🔧",
            "Security": "🔒",
            "Power": "🔋"
        }
        return category_icons.get(category, "📊")
    
    def generate_rich_dashboard(self) -> Panel:
        """Generate rich formatted decisions dashboard"""
        decisions = self.decisions_engine.analyze_system_security()
        summary = self.decisions_engine.get_security_summary()
        
        # Create main layout
        layout = Layout()
        
        # Header with summary
        header_text = Text()
        header_text.append("🔍 BLUX Guard Decisions Engine", style="bold cyan")
        header_text.append(f" • {PLATFORM.upper()}", style="bold magenta")
        header_text.append(f" • {summary['total_decisions']} decisions", style="bold white")
        
        header_panel = Panel(header_text, box=box.ROUNDED, style="bold blue")
        
        # Summary statistics
        summary_content = f"""
📈 Security Summary:
  🔴 Critical: {summary['severity_counts']['critical']}
  🟡 Warnings: {summary['severity_counts']['warning']}
  🟢 Normal: {summary['severity_counts']['normal']}
  🔵 Info: {summary['severity_counts']['info']}
  ❌ Errors: {summary['severity_counts']['error']}
"""
        summary_panel = Panel(summary_content, title="📊 Summary", box=box.SIMPLE)
        
        # Decisions table
        table = Table(title="🎯 Security Decisions", box=box.ROUNDED, show_header=True)
        table.add_column("Category", style="cyan", width=8)
        table.add_column("Decision", style="white", min_width=25)
        table.add_column("Metric", style="green", width=12)
        table.add_column("Severity", justify="center", style="red", width=10)
        
        if not decisions:
            table.add_row("No", "decisions", "available", "N/A")
        else:
            for decision in decisions[:15]:  # Show top 15 decisions
                category_icon = self._get_category_icon(decision['category'])
                severity_style = self._get_severity_style(decision['severity'])
                
                table.add_row(
                    f"{category_icon} {decision['category']}",
                    decision['decision'][:24],
                    decision['metric'],
                    Text(decision['severity'].upper(), style=severity_style)
                )
        
        # Security context panel
        if self.decisions_engine.privilege_mgr:
            privilege_info = self.decisions_engine.privilege_mgr.get_privilege_info()
            security_text = Text()
            security_text.append("🔒 Security Context:\n", style="bold")
            security_text.append(f"Mode: {'ROOT' if privilege_info['is_root'] else 'USER'}\n")
            security_text.append(f"Platform: {PLATFORM.upper()}\n")
            
            if not privilege_info['is_root']:
                security_text.append("\n⚠️  Some features limited in user mode", style="yellow")
            
            security_panel = Panel(security_text, box=box.SIMPLE, style="dim")
            
            # Layout with security
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(summary_panel, size=5),
                Layout(table, size=12),
                Layout(security_panel, size=4)
            )
        else:
            # Layout without security
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(summary_panel, size=5),
                Layout(table, size=16)
            )
        
        return Panel(layout, title="BLUX Guard Security Monitoring", box=box.DOUBLE_EDGE)
    
    def generate_basic_dashboard(self) -> str:
        """Generate basic console dashboard for environments without rich"""
        decisions = self.decisions_engine.analyze_system_security()
        summary = self.decisions_engine.get_security_summary()
        
        output = []
        output.append("=" * 80)
        output.append("              BLUX Guard Decisions Engine")
        output.append(f"         Platform: {PLATFORM} • Decisions: {summary['total_decisions']}")
        output.append("=" * 80)
        
        # Summary
        output.append(f"Summary: 🔴{summary['severity_counts']['critical']} 🟡{summary['severity_counts']['warning']} 🟢{summary['severity_counts']['normal']} 🔵{summary['severity_counts']['info']}")
        output.append("-" * 80)
        
        # Decisions table
        output.append(f"{'Category':<10} {'Decision':<25} {'Metric':<12} {'Severity':<10}")
        output.append("-" * 80)
        
        if not decisions:
            output.append("No decisions available")
        else:
            for decision in decisions[:15]:
                output.append(f"{decision['category']:<10} {decision['decision'][:24]:<25} {decision['metric']:<12} {decision['severity'].upper():<10}")
        
        output.append("=" * 80)
        output.append("Press Ctrl+C to exit")
        
        return "\n".join(output)
    
    def run(self):
        """Run the decisions view"""
        if not PSUTIL_AVAILABLE:
            console.print("[red]❌ psutil not available - decisions engine cannot run[/red]")
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
            logger.error(f"Decisions view error: {e}")
            console.print(f"[red]❌ Engine error: {e}[/red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BLUX Guard Decisions Engine")
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
        view = DecisionsView(refresh_interval=args.interval)
        view.run()
    except KeyboardInterrupt:
        print("\n👋 Decisions Engine stopped by user")
    except Exception as e:
        logger.error(f"Failed to start decisions engine: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
