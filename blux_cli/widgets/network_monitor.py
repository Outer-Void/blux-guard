#!/usr/bin/env python3
"""
BLUX Guard Network Monitor
Cross-platform network monitoring with security integration
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import time
import signal
import logging
import platform
import socket
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
    logger.warning("psutil not available - network monitoring will be limited")

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


class NetworkAnalyzer:
    """
    Cross-platform network analysis with security context
    """
    
    def __init__(self):
        self.privilege_mgr = None
        self.previous_io = None
        self.interface_history = {}
        
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception as e:
                logger.warning(f"Failed to initialize privilege manager: {e}")
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """
        Get network interfaces with enhanced information
        """
        if not PSUTIL_AVAILABLE:
            return []
        
        interfaces = []
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for iface, addresses in addrs.items():
                # Address information
                ipv4_addrs = []
                ipv6_addrs = []
                mac_addr = None
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        ipv4_addrs.append(addr.address)
                    elif addr.family == socket.AF_INET6:  # IPv6
                        # Filter out link-local addresses
                        if not addr.address.startswith("fe80:"):
                            ipv6_addrs.append(addr.address)
                    elif addr.family == psutil.AF_LINK:  # MAC address
                        mac_addr = addr.address
                
                # Interface status
                status_info = "N/A"
                speed_info = "N/A"
                if iface in stats:
                    stat = stats[iface]
                    status_info = "UP" if stat.isup else "DOWN"
                    speed_info = f"{stat.speed}Mbps" if stat.speed > 0 else "N/A"
                
                # IO statistics with rate calculation
                io_info = self._get_interface_io(iface, io_counters.get(iface))
                
                # Security assessment
                security_level = self._assess_interface_security(iface, ipv4_addrs, ipv6_addrs)
                
                interfaces.append({
                    "interface": iface,
                    "ipv4": ", ".join(ipv4_addrs) if ipv4_addrs else "None",
                    "ipv6": ", ".join(ipv6_addrs) if ipv6_addrs else "None",
                    "mac": mac_addr or "N/A",
                    "status": status_info,
                    "speed": speed_info,
                    "security_level": security_level,
                    "io_stats": io_info
                })
            
            return sorted(interfaces, key=lambda x: x['interface'])
            
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            return []
    
    def _get_interface_io(self, iface: str, io_counter) -> Dict[str, Any]:
        """Get interface IO statistics with rate calculation"""
        current_time = time.time()
        current_io = {
            'bytes_sent': getattr(io_counter, 'bytes_sent', 0) if io_counter else 0,
            'bytes_recv': getattr(io_counter, 'bytes_recv', 0) if io_counter else 0,
            'packets_sent': getattr(io_counter, 'packets_sent', 0) if io_counter else 0,
            'packets_recv': getattr(io_counter, 'packets_recv', 0) if io_counter else 0,
            'timestamp': current_time
        }
        
        # Calculate rates
        rates = {'sent_rate': 0, 'recv_rate': 0}
        if iface in self.interface_history:
            previous = self.interface_history[iface]
            time_diff = current_time - previous['timestamp']
            
            if time_diff > 0:
                bytes_sent_diff = current_io['bytes_sent'] - previous['bytes_sent']
                bytes_recv_diff = current_io['bytes_recv'] - previous['bytes_recv']
                
                rates['sent_rate'] = bytes_sent_diff / time_diff  # bytes per second
                rates['recv_rate'] = bytes_recv_diff / time_diff  # bytes per second
        
        # Update history
        self.interface_history[iface] = current_io
        
        return {
            'bytes_sent': current_io['bytes_sent'],
            'bytes_recv': current_io['bytes_recv'],
            'packets_sent': current_io['packets_sent'],
            'packets_recv': current_io['packets_recv'],
            'sent_rate': rates['sent_rate'],
            'recv_rate': rates['recv_rate']
        }
    
    def _assess_interface_security(self, iface: str, ipv4_addrs: List[str], ipv6_addrs: List[str]) -> str:
        """Assess security level of network interface"""
        # Common insecure interface patterns
        insecure_patterns = [
            'tun', 'tap',  # VPN interfaces
            'docker', 'br-', 'veth',  # Container networks
            'virbr', 'vboxnet',  # Virtual machine networks
        ]
        
        # Check for localhost only (secure)
        if iface in ['lo', 'loopback']:
            return "secure"
        
        # Check for potentially insecure interfaces
        if any(pattern in iface.lower() for pattern in insecure_patterns):
            return "warning"
        
        # Check for public IP addresses
        for ip in ipv4_addrs + ipv6_addrs:
            if self._is_public_ip(ip):
                return "public"
        
        return "normal"
    
    def _is_public_ip(self, ip: str) -> bool:
        """Check if IP address is public"""
        try:
            # Common private network ranges
            private_ranges = [
                ('10.', True),
                ('172.16.', True), ('172.17.', True), ('172.18.', True), ('172.19.', True),
                ('172.20.', True), ('172.21.', True), ('172.22.', True), ('172.23.', True),
                ('172.24.', True), ('172.25.', True), ('172.26.', True), ('172.27.', True),
                ('172.28.', True), ('172.29.', True), ('172.30.', True), ('172.31.', True),
                ('192.168.', True),
                ('169.254.', True),  # Link-local
                ('127.', True),  # Loopback
            ]
            
            for prefix, is_private in private_ranges:
                if ip.startswith(prefix):
                    return not is_private
            
            # IPv6 private ranges
            if ip.startswith('fc') or ip.startswith('fd') or ip.startswith('fe80:'):
                return False
            
            return True
        except:
            return False
    
    def get_network_connections(self, max_connections: int = 10) -> List[Dict[str, Any]]:
        """
        Get active network connections with security context
        """
        if not PSUTIL_AVAILABLE:
            return []
        
        connections = []
        try:
            # Only get connections if we have sufficient privileges
            if self.privilege_mgr and self.privilege_mgr.is_root:
                net_conns = psutil.net_connections(kind='inet')
            else:
                # Non-root users may have limited access
                net_conns = []
                try:
                    net_conns = psutil.net_connections(kind='inet')
                except (psutil.AccessDenied, PermissionError):
                    logger.debug("Insufficient privileges for network connections")
                    return []
            
            for conn in net_conns[:max_connections]:
                try:
                    conn_info = {
                        "family": self._get_address_family(conn.family),
                        "type": self._get_connection_type(conn.type),
                        "local_addr": self._format_address(conn.laddr),
                        "remote_addr": self._format_address(conn.raddr),
                        "status": getattr(conn, 'status', 'N/A'),
                        "pid": getattr(conn, 'pid', None),
                    }
                    
                    # Security assessment
                    conn_info["security_level"] = self._assess_connection_security(conn_info)
                    connections.append(conn_info)
                    
                except (psutil.NoSuchProcess, AttributeError):
                    continue
            
            return connections
            
        except Exception as e:
            logger.error(f"Error getting network connections: {e}")
            return []
    
    def _get_address_family(self, family) -> str:
        """Convert address family to string"""
        family_map = {
            socket.AF_INET: 'IPv4',
            socket.AF_INET6: 'IPv6',
        }
        return family_map.get(family, str(family))
    
    def _get_connection_type(self, conn_type) -> str:
        """Convert connection type to string"""
        type_map = {
            socket.SOCK_STREAM: 'TCP',
            socket.SOCK_DGRAM: 'UDP',
        }
        return type_map.get(conn_type, str(conn_type))
    
    def _format_address(self, addr) -> str:
        """Format network address"""
        if not addr:
            return "N/A"
        return f"{addr.ip}:{addr.port}" if hasattr(addr, 'port') else str(addr.ip)
    
    def _assess_connection_security(self, conn_info: Dict[str, Any]) -> str:
        """Assess security level of network connection"""
        remote_addr = conn_info.get('remote_addr', '')
        
        # Check common ports for increased scrutiny
        port = int(remote_addr.split(':')[1]) if remote_addr != 'N/A' and ':' in remote_addr else None
        if port:
            security_level = self._assess_port_security(port)
            if security_level != "normal":
                return security_level
        
        # Established connections to remote systems
        if conn_info.get('status') == 'ESTABLISHED' and remote_addr != 'N/A':
            if self._is_public_ip(remote_addr.split(':')[0]):
                return "public"
            else:
                return "established"
        
        # Listening services
        if conn_info.get('status') == 'LISTEN':
            return "listening"
        
        return "normal"
    
    def _assess_port_security(self, port: int) -> str:
        """Assess security level based on port number"""
        # Known malicious ports
        malicious_ports = [21, 22, 23, 25, 135, 139, 445, 1433, 3306, 3389, 8080]
        if port in malicious_ports:
            return "warning"
        
        # Common secure ports
        secure_ports = [80, 443]
        if port in secure_ports:
            return "secure"
        
        return "normal"
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        if not PSUTIL_AVAILABLE:
            return {}
        
        try:
            io = psutil.net_io_counters()
            interfaces = self.get_network_interfaces()
            
            # Calculate total rates
            total_sent_rate = sum(iface['io_stats']['sent_rate'] for iface in interfaces)
            total_recv_rate = sum(iface['io_stats']['recv_rate'] for iface in interfaces)
            
            return {
                "total_bytes_sent": getattr(io, 'bytes_sent', 0),
                "total_bytes_recv": getattr(io, 'bytes_recv', 0),
                "total_packets_sent": getattr(io, 'packets_sent', 0),
                "total_packets_recv": getattr(io, 'packets_recv', 0),
                "total_sent_rate": total_sent_rate,
                "total_recv_rate": total_recv_rate,
                "interface_count": len(interfaces),
                "up_interfaces": len([iface for iface in interfaces if iface['status'] == 'UP']),
                "active_connections": len(self.get_network_connections()),
                "platform": PLATFORM
            }
        except Exception as e:
            logger.error(f"Error getting network statistics: {e}")
            return {}


class NetworkMonitor:
    """
    Enhanced Network Monitor with security integration
    """
    
    def __init__(self, refresh_interval: float = 2.0):
        self.refresh_interval = refresh_interval
        self.analyzer = NetworkAnalyzer()
        self.running = True
        
        # Signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Network Monitor initialized for platform: {PLATFORM}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if RICH_AVAILABLE:
            console.print("\n[yellow]🛑 Shutting down Network Monitor...[/yellow]")
        else:
            print("\n🛑 Shutting down Network Monitor...")
        self.running = False
    
    def _format_bytes(self, size: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _format_rate(self, rate: float) -> str:
        """Format data rate"""
        return self._format_bytes(rate) + "/s"
    
    def _get_status_style(self, status: str) -> str:
        """Get color style for interface status"""
        if "UP" in status:
            return "green"
        elif "DOWN" in status:
            return "red"
        else:
            return "yellow"
    
    def _get_security_style(self, security_level: str) -> str:
        """Get color style for security level"""
        security_styles = {
            "secure": "green",
            "normal": "blue",
            "warning": "yellow",
            "public": "red",
            "established": "cyan",
            "listening": "magenta"
        }
        return security_styles.get(security_level, "white")
    
    def _get_security_indicator(self, security_level: str) -> str:
        """Get security indicator icon"""
        security_indicators = {
            "secure": "🟢",
            "normal": "🔵",
            "warning": "🟡",
            "public": "🔴",
            "established": "🟣",
            "listening": "🟠"
        }
        return security_indicators.get(security_level, "⚪")
    
    def generate_rich_dashboard(self) -> Panel:
        """Generate rich formatted network dashboard"""
        interfaces = self.analyzer.get_network_interfaces()
        connections = self.analyzer.get_network_connections()
        stats = self.analyzer.get_network_statistics()
        
        # Create main layout
        layout = Layout()
        
        # Header with system info
        header_text = Text()
        header_text.append("🌐 BLUX Guard Network Monitor", style="bold cyan")
        header_text.append(f" • {PLATFORM.upper()}", style="bold magenta")
        if self.analyzer.privilege_mgr:
            priv_info = self.analyzer.privilege_mgr.get_privilege_info()
            header_text.append(f" • {priv_info['privilege_level'].upper()}", 
                             style="bold red" if priv_info['is_root'] else "bold green")
        
        header_panel = Panel(header_text, box=box.ROUNDED, style="bold blue")
        
        # Network statistics panel
        if stats:
            stats_content = f"""
Total Traffic: ↑{self._format_bytes(stats['total_bytes_sent'])} ↓{self._format_bytes(stats['total_bytes_recv'])}
Current Rate: ↑{self._format_rate(stats['total_sent_rate'])} ↓{self._format_rate(stats['total_recv_rate'])}
Interfaces: {stats['up_interfaces']}/{stats['interface_count']} up
Connections: {stats['active_connections']} active
"""
            stats_panel = Panel(stats_content, title="📊 Network Statistics", box=box.SIMPLE)
        else:
            stats_panel = Panel("[red]Network statistics unavailable[/red]", title="📊 Network Statistics")
        
        # Interfaces table
        iface_table = Table(title="🔌 Network Interfaces", box=box.ROUNDED, show_header=True)
        iface_table.add_column("Sec", style="white", width=3)
        iface_table.add_column("Interface", style="cyan", width=12)
        iface_table.add_column("IPv4", style="green", min_width=15)
        iface_table.add_column("Status", justify="center", style="red", width=10)
        iface_table.add_column("Speed", justify="center", style="yellow", width=8)
        iface_table.add_column("Rate ↑", justify="right", style="magenta", width=10)
        iface_table.add_column("Rate ↓", justify="right", style="blue", width=10)
        
        if not interfaces:
            iface_table.add_row("", "No", "interfaces", "found", "N/A", "N/A", "N/A")
        else:
            for iface in interfaces:
                security_indicator = self._get_security_indicator(iface['security_level'])
                status_style = self._get_status_style(iface['status'])
                
                iface_table.add_row(
                    security_indicator,
                    iface['interface'],
                    iface['ipv4'][:14],
                    Text(iface['status'], style=status_style),
                    iface['speed'],
                    self._format_rate(iface['io_stats']['sent_rate']),
                    self._format_rate(iface['io_stats']['recv_rate'])
                )
        
        # Connections table (if available)
        if connections and self.analyzer.privilege_mgr and self.analyzer.privilege_mgr.is_root:
            conn_table = Table(title="🔗 Active Connections", box=box.ROUNDED, show_header=True)
            conn_table.add_column("Sec", style="white", width=3)
            conn_table.add_column("Protocol", style="cyan", width=8)
            conn_table.add_column("Local", style="green", min_width=18)
            conn_table.add_column("Remote", style="magenta", min_width=18)
            conn_table.add_column("Status", style="yellow", width=12)
            conn_table.add_column("PID", style="blue", width=8)
            
            for conn in connections:
                security_indicator = self._get_security_indicator(conn['security_level'])
                security_style = self._get_security_style(conn['security_level'])
                
                conn_table.add_row(
                    security_indicator,
                    f"{conn['family']}/{conn['type']}",
                    conn['local_addr'][:17],
                    conn['remote_addr'][:17],
                    Text(conn['status'], style=security_style),
                    str(conn['pid']) if conn['pid'] else "N/A"
                )
            
            # Layout with connections
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(stats_panel, size=5),
                Layout(iface_table, size=10),
                Layout(conn_table, size=8)
            )
        else:
            # Layout without connections
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(stats_panel, size=5),
                Layout(iface_table, size=12)
            )
        
        # Security context panel
        if self.analyzer.privilege_mgr:
            privilege_info = self.analyzer.privilege_mgr.get_privilege_info()
            security_text = Text()
            security_text.append("🔒 Security Context:\n", style="bold")
            security_text.append(f"Mode: {'ROOT' if privilege_info['is_root'] else 'USER'}\n")
            
            if not self.analyzer.privilege_mgr.is_root:
                security_text.append("⚠️  Connection details limited in user mode\n", style="yellow")
            
            security_text.append("\nSecurity Legend:\n", style="bold")
            security_text.append("🟢 Secure  🔵 Normal  🟡 Warning  🔴 Public\n", style="dim")
            security_text.append("🟣 Established  🟠 Listening", style="dim")
            
            security_panel = Panel(security_text, box=box.SIMPLE, style="dim")
            
            # Add security panel to layout
            if connections and self.analyzer.privilege_mgr.is_root:
                layout.split_row(
                    Layout(layout, size=70),
                    Layout(security_panel, size=30)
                )
            else:
                layout.split_column(
                    layout,
                    Layout(security_panel, size=6)
                )
        
        return Panel(layout, title="BLUX Guard Security Monitoring", box=box.DOUBLE_EDGE)
    
    def generate_basic_dashboard(self) -> str:
        """Generate basic console dashboard for environments without rich"""
        interfaces = self.analyzer.get_network_interfaces()
        stats = self.analyzer.get_network_statistics()
        
        output = []
        output.append("=" * 80)
        output.append("              BLUX Guard Network Monitor")
        output.append(f"         Platform: {PLATFORM}")
        if self.analyzer.privilege_mgr:
            priv_info = self.analyzer.privilege_mgr.get_privilege_info()
            output.append(f"         Mode: {'ROOT' if privilege_info['is_root'] else 'USER'}")
        output.append("=" * 80)
        
        # Network statistics
        if stats:
            output.append(f"Total: ↑{self._format_bytes(stats['total_bytes_sent'])} ↓{self._format_bytes(stats['total_bytes_recv'])}")
            output.append(f"Rate: ↑{self._format_rate(stats['total_sent_rate'])} ↓{self._format_rate(stats['total_recv_rate'])}")
            output.append(f"Interfaces: {stats['up_interfaces']}/{stats['interface_count']} up")
        output.append("-" * 80)
        
        # Interface table header
        output.append(f"{'Sec':<3} {'Interface':<12} {'IPv4':<15} {'Status':<10} {'Speed':<8} {'Rate ↑':<10} {'Rate ↓':<10}")
        output.append("-" * 80)
        
        if not interfaces:
            output.append("No network interfaces found")
        else:
            for iface in interfaces:
                security_indicator = self._get_security_indicator(iface['security_level'])
                output.append(f"{security_indicator:<3} {iface['interface']:<12} {iface['ipv4'][:14]:<15} "
                            f"{iface['status']:<10} {iface['speed']:<8} "
                            f"{self._format_rate(iface['io_stats']['sent_rate']):<10} "
                            f"{self._format_rate(iface['io_stats']['recv_rate']):<10}")
        
        output.append("=" * 80)
        output.append("Legend: 🟢 Secure  🔵 Normal  🟡 Warning  🔴 Public")
        output.append("Press Ctrl+C to exit")
        
        return "\n".join(output)
    
    def run(self):
        """Run the network monitor"""
        if not PSUTIL_AVAILABLE:
            console.print("[red]❌ psutil not available - network monitor cannot run[/red]")
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
            logger.error(f"Network monitor error: {e}")
            console.print(f"[red]❌ Monitor error: {e}[/red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BLUX Guard Network Monitor")
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
        monitor = NetworkMonitor(refresh_interval=args.interval)
        monitor.run()
    except KeyboardInterrupt:
        print("\n👋 Network Monitor stopped by user")
    except Exception as e:
        logger.error(f"Failed to start network monitor: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
