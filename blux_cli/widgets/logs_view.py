#!/usr/bin/env python3
"""
BLUX Guard Logs Viewer
Cross-platform log monitoring with security integration
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
from typing import List, Dict, Optional, Any, Callable

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
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.table import Table
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

class LogAnalyzer:
    """
    Cross-platform log analysis with security context
    """
    
    def __init__(self):
        self.privilege_mgr = None
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception as e:
                logger.warning(f"Failed to initialize privilege manager: {e}")
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def get_available_logs(self, log_directory: Path) -> List[Dict[str, Any]]:
        """
        Get list of available log files with metadata
        """
        logs = []
        
        if not log_directory.exists():
            log_directory.mkdir(parents=True, exist_ok=True)
            return logs
        
        try:
            for log_file in log_directory.rglob("*.log"):
                try:
                    stat = log_file.stat()
                    
                    # Security check - only include readable files
                    if not os.access(log_file, os.R_OK):
                        continue
                    
                    # Get file size
                    size_kb = stat.st_size / 1024
                    
                    # Determine log type from filename and path
                    log_type = self._classify_log_file(log_file)
                    
                    # Security assessment
                    security_level = self._assess_log_security(log_file, log_type)
                    
                    logs.append({
                        "path": log_file,
                        "name": log_file.name,
                        "relative_path": log_file.relative_to(log_directory),
                        "size_kb": round(size_kb, 1),
                        "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime)),
                        "type": log_type,
                        "security_level": security_level,
                        "readable": True
                    })
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not access log file {log_file}: {e}")
                    continue
            
            return sorted(logs, key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error scanning log directory: {e}")
            return []
    
    def _classify_log_file(self, log_file: Path) -> str:
        """Classify log file type based on name and path"""
        filename = log_file.name.lower()
        path_parts = [part.lower() for part in log_file.parts]
        
        # Security logs
        security_indicators = ['security', 'auth', 'login', 'sudo', 'fail', 'denied']
        if any(indicator in filename for indicator in security_indicators):
            return "security"
        
        # System logs
        system_indicators = ['system', 'kernel', 'boot', 'dmesg', 'syslog']
        if any(indicator in filename or any(indicator in path_parts) for indicator in system_indicators):
            return "system"
        
        # Application logs
        app_indicators = ['app', 'application', 'service', 'daemon']
        if any(indicator in filename for indicator in app_indicators):
            return "application"
        
        # Network logs
        network_indicators = ['network', 'net', 'firewall', 'iptables', 'ufw']
        if any(indicator in filename for indicator in network_indicators):
            return "network"
        
        # Default classification
        return "general"
    
    def _assess_log_security(self, log_file: Path, log_type: str) -> str:
        """Assess security level of log file"""
        # Security logs are high sensitivity
        if log_type == "security":
            return "high"
        
        # System logs may contain sensitive information
        if log_type == "system":
            return "medium"
        
        # Check file permissions
        try:
            stat = log_file.stat()
            # Check if file is world-readable
            if stat.st_mode & 0o004:
                return "low"  # World-readable files are less sensitive
        except OSError:
            pass
        
        return "normal"
    
    def analyze_log_patterns(self, log_content: str) -> Dict[str, Any]:
        """
        Analyze log content for patterns and security events
        """
        patterns = {
            "errors": 0,
            "warnings": 0,
            "security_events": 0,
            "recent_activity": 0
        }
        
        lines = log_content.split('\n')
        patterns["total_lines"] = len(lines)
        
        for line in lines:
            line_lower = line.lower()
            
            # Error patterns
            if any(error in line_lower for error in ['error', 'exception', 'failed', 'failure']):
                patterns["errors"] += 1
            
            # Warning patterns
            if any(warning in line_lower for warning in ['warning', 'warn', 'caution']):
                patterns["warnings"] += 1
            
            # Security event patterns
            security_terms = ['denied', 'unauthorized', 'forbidden', 'intrusion', 'breach', 'attack']
            if any(term in line_lower for term in security_terms):
                patterns["security_events"] += 1
        
        # Calculate recent activity (last 100 lines)
        recent_lines = lines[-100:] if len(lines) > 100 else lines
        patterns["recent_activity"] = len([line for line in recent_lines if line.strip()])
        
        return patterns
    
    def get_log_file_info(self, log_file: Path) -> Dict[str, Any]:
        """Get detailed information about a log file"""
        try:
            stat = log_file.stat()
            
            return {
                "path": str(log_file),
                "size_bytes": stat.st_size,
                "size_human": self._format_file_size(stat.st_size),
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                "accessed": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_atime)),
                "permissions": oct(stat.st_mode)[-3:],
                "readable": os.access(log_file, os.R_OK),
                "writable": os.access(log_file, os.W_OK)
            }
        except OSError as e:
            return {"error": str(e)}
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class LogsViewer:
    """
    Enhanced Logs Viewer with security integration
    """
    
    def __init__(self, log_directory: Path = None, refresh_interval: float = 1.0, tail_lines: int = 50):
        self.log_directory = log_directory or _project_root / "logs"
        self.refresh_interval = refresh_interval
        self.tail_lines = tail_lines
        self.analyzer = LogAnalyzer()
        self.current_log = None
        self._last_size = 0
        self.running = True
        
        # Signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Logs Viewer initialized for platform: {PLATFORM}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if RICH_AVAILABLE:
            console.print("\n[yellow]🛑 Shutting down Logs Viewer...[/yellow]")
        else:
            print("\n🛑 Shutting down Logs Viewer...")
        self.running = False
    
    def set_current_log(self, log_file: Path):
        """Set the current log file to monitor"""
        self.current_log = log_file
        self._last_size = 0
    
    def _read_tail_lines(self, log_file: Path) -> str:
        """
        Read the last N lines from the log file with error handling
        """
        if not log_file.exists():
            return f"[red]❌ Log file not found: {log_file}[/red]"
        
        try:
            # Security check - ensure file is readable
            if not os.access(log_file, os.R_OK):
                return f"[red]❌ Permission denied: {log_file}[/red]"
            
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, 2)  # Seek to end
                current_size = f.tell()
                
                # Handle file truncation or rotation
                if current_size < self._last_size:
                    self._last_size = 0
                
                if self._last_size == 0:
                    # Read entire file and get last N lines
                    f.seek(0)
                    lines = f.readlines()
                    content = ''.join(lines[-self.tail_lines:])
                else:
                    # Read only new content
                    f.seek(self._last_size)
                    content = f.read()
                
                self._last_size = current_size
                
                if not content.strip():
                    return "[dim]📭 No new log entries...[/dim]"
                
                return content
                
        except PermissionError:
            return f"[red]❌ Permission denied: {log_file}[/red]"
        except FileNotFoundError:
            return f"[red]❌ Log file disappeared: {log_file}[/red]"
        except Exception as e:
            logger.error(f"Error reading log file {log_file}: {e}")
            return f"[red]❌ Error reading log: {e}[/red]"
    
    def _get_file_info(self, log_file: Path) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            stat = log_file.stat()
            return {
                "size_kb": stat.st_size / 1024,
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                "permissions": oct(stat.st_mode)[-3:],
                "readable": os.access(log_file, os.R_OK)
            }
        except OSError as e:
            return {"error": str(e)}
    
    def _get_security_style(self, security_level: str) -> str:
        """Get color style for security level"""
        security_styles = {
            "high": "bold red",
            "medium": "yellow",
            "normal": "green",
            "low": "blue"
        }
        return security_styles.get(security_level, "white")
    
    def generate_rich_dashboard(self) -> Panel:
        """Generate rich formatted log dashboard"""
        if not self.current_log:
            return self._generate_log_selector()
        
        # Read log content
        log_content = self._read_tail_lines(self.current_log)
        file_info = self._get_file_info(self.current_log)
        patterns = self.analyzer.analyze_log_patterns(log_content)
        
        # Create main layout
        layout = Layout()
        
        # Header with file info
        header_text = Text()
        header_text.append("📋 BLUX Guard Logs Viewer", style="bold cyan")
        header_text.append(f" • {self.current_log.name}", style="bold white")
        
        if "error" not in file_info:
            header_text.append(f" • {file_info['size_kb']:.1f} KB", style="dim")
            header_text.append(f" • {file_info['modified']}", style="dim")
        
        header_panel = Panel(header_text, box=box.ROUNDED, style="bold blue")
        
        # Log content panel
        if RICH_AVAILABLE and len(log_content) < 10000:  # Only syntax highlight smaller files
            try:
                syntax = Syntax(log_content, "log", line_numbers=True, word_wrap=True)
                content_panel = Panel(syntax, title="📜 Log Content", box=box.ROUNDED)
            except Exception:
                content_panel = Panel(log_content, title="📜 Log Content", box=box.ROUNDED)
        else:
            content_panel = Panel(log_content, title="📜 Log Content", box=box.ROUNDED)
        
        # Statistics panel
        stats_content = f"""
📊 Log Analysis:
  Total Lines: {patterns['total_lines']}
  ⚠️  Errors: {patterns['errors']}
  🔸 Warnings: {patterns['warnings']}
  🔒 Security Events: {patterns['security_events']}
  📈 Recent Activity: {patterns['recent_activity']}/100 lines
"""
        stats_panel = Panel(stats_content, title="📈 Statistics", box=box.SIMPLE)
        
        # Security context panel
        if self.analyzer.privilege_mgr:
            privilege_info = self.analyzer.privilege_mgr.get_privilege_info()
            security_text = Text()
            security_text.append("🔒 Security Context:\n", style="bold")
            security_text.append(f"Mode: {'ROOT' if privilege_info['is_root'] else 'USER'}\n")
            
            if not file_info.get('readable', False):
                security_text.append("⚠️  Log file not readable\n", style="yellow")
            
            security_text.append(f"Permissions: {file_info.get('permissions', 'N/A')}\n")
            
            security_panel = Panel(security_text, box=box.SIMPLE, style="dim")
            
            # Layout with security
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(content_panel, size=12),
                Layout(stats_panel, size=5),
                Layout(security_panel, size=4)
            )
        else:
            # Layout without security
            layout.split_column(
                Layout(header_panel, size=3),
                Layout(content_panel, size=14),
                Layout(stats_panel, size=7)
            )
        
        return Panel(layout, title="BLUX Guard Security Monitoring", box=box.DOUBLE_EDGE)
    
    def _generate_log_selector(self) -> Panel:
        """Generate log file selection interface"""
        available_logs = self.analyzer.get_available_logs(self.log_directory)
        
        if RICH_AVAILABLE:
            table = Table(title="📁 Available Log Files", box=box.ROUNDED, show_header=True)
            table.add_column("Type", style="cyan", width=8)
            table.add_column("File", style="white", min_width=20)
            table.add_column("Size", style="green", width=10)
            table.add_column("Modified", style="yellow", width=16)
            table.add_column("Security", style="red", width=8)
            
            if not available_logs:
                table.add_row("No", "log files", "found", "N/A", "N/A")
            else:
                for log in available_logs:
                    security_style = self._get_security_style(log['security_level'])
                    table.add_row(
                        log['type'][:7],
                        log['name'],
                        f"{log['size_kb']} KB",
                        log['modified'],
                        Text(log['security_level'].upper(), style=security_style)
                    )
            
            content = table
        else:
            content = "Available Log Files:\n" + "\n".join(
                f"  {log['name']} ({log['type']}, {log['size_kb']}KB)"
                for log in available_logs
            )
        
        return Panel(
            content,
            title="📋 BLUX Guard Logs Viewer - File Selector",
            subtitle="[dim]Select a log file to monitor | Press Ctrl+C to exit[/dim]",
            border_style="blue"
        )
    
    def generate_basic_dashboard(self) -> str:
        """Generate basic console dashboard for environments without rich"""
        if not self.current_log:
            available_logs = self.analyzer.get_available_logs(self.log_directory)
            
            output = []
            output.append("=" * 70)
            output.append("              BLUX Guard Logs Viewer - File Selector")
            output.append("=" * 70)
            
            if not available_logs:
                output.append("No log files found")
            else:
                for log in available_logs:
                    output.append(f"{log['type']:>8} | {log['name']:<20} | {log['size_kb']:>6} KB | {log['modified']}")
            
            output.append("=" * 70)
            output.append("Select a log file using --log parameter")
            return "\n".join(output)
        
        # Show log content
        log_content = self._read_tail_lines(self.current_log)
        file_info = self._get_file_info(self.current_log)
        
        output = []
        output.append("=" * 70)
        output.append(f"BLUX Guard Logs Viewer - {self.current_log.name}")
        if "error" not in file_info:
            output.append(f"Size: {file_info['size_kb']:.1f} KB | Modified: {file_info['modified']}")
        output.append("=" * 70)
        output.append(log_content)
        output.append("=" * 70)
        output.append("Press Ctrl+C to exit")
        
        return "\n".join(output)
    
    def run(self):
        """Run the logs viewer"""
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
            logger.error(f"Logs viewer error: {e}")
            console.print(f"[red]❌ Viewer error: {e}[/red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BLUX Guard Logs Viewer")
    parser.add_argument(
        "--log", "-l",
        type=Path,
        help="Path to specific log file to monitor"
    )
    parser.add_argument(
        "--directory", "-d",
        type=Path,
        default=_project_root / "logs",
        help="Log directory to scan (default: ./logs)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=1.0,
        help="Refresh interval in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--tail", "-t",
        type=int,
        default=50,
        help="Number of lines to show from the end (default: 50)"
    )
    parser.add_argument(
        "--basic", "-b",
        action="store_true",
        help="Force basic console mode"
    )
    
    args = parser.parse_args()
    
    try:
        viewer = LogsViewer(
            log_directory=args.directory,
            refresh_interval=args.interval,
            tail_lines=args.tail
        )
        
        if args.log:
            viewer.set_current_log(args.log)
        
        viewer.run()
    except KeyboardInterrupt:
        print("\n👋 Logs Viewer stopped by user")
    except Exception as e:
        logger.error(f"Failed to start logs viewer: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
