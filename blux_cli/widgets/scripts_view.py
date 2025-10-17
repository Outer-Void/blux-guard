#!/usr/bin/env python3
"""
BLUX Guard Scripts Explorer
Cross-platform script management with security controls
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path
from datetime import datetime
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
    from textual.app import App, ComposeResult
    from textual.containers import Vertical, Horizontal, Container
    from textual.widgets import Header, Footer, Button, ListView, ListItem, Static, Label, Input
    from textual.reactive import reactive
    from textual.binding import Binding
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.panel import Panel
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    logger.warning("Textual not available - scripts view requires: pip install textual")

# Security integration
try:
    from blux_modules.security.privilege_manager import PrivilegeManager
    from blux_modules.security.auth_system import AuthSystem
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Platform detection
def detect_platform() -> str:
    """Detect current platform"""
    import platform
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

class ScriptManager:
    """
    Cross-platform script management with security controls
    """
    
    def __init__(self):
        self.privilege_mgr = None
        self.auth_system = None
        self.scripts_dir = self._get_scripts_directory()
        
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
                self.auth_system = AuthSystem()
            except Exception as e:
                logger.warning(f"Security systems not available: {e}")
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()
    
    def _get_scripts_directory(self) -> Path:
        """Get platform-appropriate scripts directory"""
        # Try project scripts directory first
        project_scripts = _project_root / "scripts"
        if project_scripts.exists():
            return project_scripts
        
        # Try user home directory
        home_scripts = Path.home() / "blux-guard" / "scripts"
        home_scripts.mkdir(parents=True, exist_ok=True)
        return home_scripts
    
    def get_scripts_list(self) -> List[Dict[str, Any]]:
        """Get list of available scripts with metadata"""
        scripts = []
        
        if not self.scripts_dir.exists():
            self.scripts_dir.mkdir(parents=True, exist_ok=True)
            return scripts
        
        for script_file in self.scripts_dir.iterdir():
            if script_file.is_file():
                try:
                    # Get file permissions
                    stat = script_file.stat()
                    is_executable = os.access(script_file, os.X_OK)
                    
                    # Get file size
                    size_kb = stat.st_size / 1024
                    
                    # Determine script type
                    script_type = self._detect_script_type(script_file)
                    
                    # Check security context
                    requires_root = self._check_root_requirement(script_file)
                    
                    scripts.append({
                        "name": script_file.name,
                        "path": script_file,
                        "size_kb": round(size_kb, 1),
                        "executable": is_executable,
                        "type": script_type,
                        "requires_root": requires_root,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "security_level": self._get_security_level(script_file)
                    })
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not read script {script_file}: {e}")
                    continue
        
        return sorted(scripts, key=lambda x: x["name"])
    
    def _detect_script_type(self, script_path: Path) -> str:
        """Detect script type from file extension and content"""
        extension = script_path.suffix.lower()
        
        type_map = {
            '.sh': 'Shell Script',
            '.bash': 'Bash Script',
            '.py': 'Python Script',
            '.js': 'JavaScript',
            '.rb': 'Ruby Script',
            '.pl': 'Perl Script',
            '.ps1': 'PowerShell',
            '.bat': 'Batch File',
            '.cmd': 'Command File',
        }
        
        # Check shebang for additional info
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    if 'python' in first_line:
                        return 'Python Script'
                    elif 'bash' in first_line or 'sh' in first_line:
                        return 'Shell Script'
                    elif 'perl' in first_line:
                        return 'Perl Script'
                    elif 'ruby' in first_line:
                        return 'Ruby Script'
        except (OSError, UnicodeDecodeError):
            pass
        
        return type_map.get(extension, 'Unknown Script')
    
    def _check_root_requirement(self, script_path: Path) -> bool:
        """Check if script likely requires root privileges"""
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
            # Common root-requiring patterns
            root_patterns = [
                'sudo ', 'su -c', 'pkexec', 'gksudo',
                '/etc/', '/var/log/', '/sys/', '/proc/',
                'iptables', 'ufw', 'firewall-cmd',
                'systemctl', 'service ', 'chown ', 'chmod ',
                'mount ', 'umount ', 'fdisk ', 'mkfs.',
                'useradd', 'userdel', 'groupadd', 'passwd'
            ]
            
            return any(pattern in content for pattern in root_patterns)
            
        except (OSError, UnicodeDecodeError):
            return False
    
    def _get_security_level(self, script_path: Path) -> str:
        """Determine security level for script"""
        requires_root = self._check_root_requirement(script_path)
        
        privilege_info = self.privilege_mgr.get_privilege_info()
        if requires_root:
            if privilege_info and privilege_info['is_root']:
                return "high"  # Root available and required
            else:
                return "warning"  # Root required but not available
        else:
            return "normal"  # No special privileges needed
    
    async def execute_script(self, script_info: Dict[str, Any], 
                           log_callback: Callable[[str], None],
                           require_auth: bool = True) -> bool:
        """
        Execute a script with security controls
        Returns True if execution was successful
        """
        script_path = script_info["path"]
        
        # Security checks
        if require_auth and self.auth_system:
            if not self.auth_system.authenticate():
                await log_callback("[red]❌ Authentication failed - script execution blocked[/red]")
                return False
        
        privilege_info = self.privilege_mgr.get_privilege_info()
        if script_info["requires_root"] and privilege_info and not privilege_info['is_root']:
            await log_callback("[yellow]⚠️  Script may require root privileges - some operations may fail[/yellow]")
        
        if not script_info["executable"]:
            await log_callback("[yellow]⚠️  Script is not executable - attempting to run with interpreter[/yellow]")
        
        await log_callback(f"[bold]🚀 Executing: {script_info['name']}[/bold]")
        await log_callback(f"📁 Type: {script_info['type']}")
        await log_callback(f"🔒 Security: {script_info['security_level'].upper()}")
        await log_callback("-" * 40)
        
        try:
            # Determine execution method based on script type
            if script_info["type"] == "Python Script" and not script_info["executable"]:
                cmd = [sys.executable, str(script_path)]
            elif script_info["type"] == "Shell Script" and not script_info["executable"]:
                cmd = ["sh", str(script_path)]
            else:
                cmd = [str(script_path)]
            
            # Execute script
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(script_path.parent)
            )
            
            stdout, stderr = await process.communicate()
            return_code = process.returncode
            
            # Log output
            if stdout:
                await log_callback(f"[green]STDOUT:\n{stdout.decode('utf-8', errors='replace')}[/green]")
            if stderr:
                await log_callback(f"[yellow]STDERR:\n{stderr.decode('utf-8', errors='replace')}[/yellow]")
            
            if return_code == 0:
                await log_callback(f"[green]✅ Script completed successfully (exit code: {return_code})[/green]")
                return True
            else:
                await log_callback(f"[red]❌ Script failed (exit code: {return_code})[/red]")
                return False
                
        except Exception as e:
            await log_callback(f"[red]❌ Execution error: {str(e)}[/red]")
            return False
    
    def view_script_content(self, script_path: Path) -> str:
        """Get script content for viewing"""
        try:
            with open(script_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        except (OSError, UnicodeDecodeError) as e:
            return f"Error reading script: {str(e)}"
    
    def create_sample_script(self, script_type: str = "python") -> bool:
        """Create a sample script for demonstration"""
        sample_content = ""
        filename = ""
        
        if script_type == "python":
            filename = "example_security_scan.py"
            sample_content = '''#!/usr/bin/env python3
"""
BLUX Guard Security Scan Example
Basic system security check script
"""

import os
import platform
import sys

def check_system_security():
    """Perform basic security checks"""
    print("🔍 BLUX Guard Security Scan")
    print("=" * 40)
    
    # System information
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # Basic security checks
    checks = [
        ("Home directory permissions", check_home_permissions()),
        ("Python path security", check_python_path()),
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    print("\\nScan completed!")

def check_home_permissions():
    """Check home directory permissions"""
    home = os.path.expanduser("~")
    try:
        stat = os.stat(home)
        return stat.st_mode & 0o022 == 0  # Should not be world-writable
    except OSError:
        return False

def check_python_path():
    """Check Python path for security"""
    safe_paths = [p for p in sys.path if p and not p.startswith('/tmp')]
    return len(safe_paths) == len(sys.path)

if __name__ == "__main__":
    check_system_security()
'''
        elif script_type == "shell":
            filename = "example_system_info.sh"
            sample_content = '''#!/bin/bash
#
# BLUX Guard System Info Script
# Basic system information gathering
#

echo "🖥️  BLUX Guard System Information"
echo "=================================="

# System info
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"

# Memory info
echo -e "\\nMemory Usage:"
free -h

# Disk info  
echo -e "\\nDisk Usage:"
df -h / | tail -1

echo -e "\\nScan completed successfully!"
'''

        if sample_content:
            script_path = self.scripts_dir / filename
            try:
                with open(script_path, 'w') as f:
                    f.write(sample_content)
                # Make executable
                script_path.chmod(0o755)
                return True
            except OSError as e:
                logger.error(f"Failed to create sample script: {e}")
                return False
        
        return False


class ScriptsViewApp(App):
    """
    Enhanced Scripts Explorer with security integration
    """
    
    CSS_PATH = "blux_cockpit.css"
    BINDINGS = [
        Binding("r", "run_script", "Run Script"),
        Binding("v", "view_script", "View Script"),
        Binding("n", "new_script", "New Sample"),
        Binding("f5", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]
    
    selected_script = reactive(None)
    script_manager = ScriptManager()
    
    def compose(self) -> ComposeResult:
        """Compose the application UI"""
        yield Header()
        
        with Container(classes="main-container"):
            # Scripts list section
            with Vertical(classes="scripts-section"):
                yield Label("📜 Available Scripts", classes="section-header")
                self.scripts_list = ListView(classes="scripts-list")
                yield self.scripts_list
            
            # Control buttons
            with Horizontal(classes="controls-section"):
                yield Button("🚀 Run Script", id="btn_run", classes="btn-primary")
                yield Button("👁️ View Script", id="btn_view", classes="btn-secondary")
                yield Button("🆕 New Sample", id="btn_new", classes="btn-secondary")
                yield Button("🔄 Refresh", id="btn_refresh", classes="btn-secondary")
            
            # Log/output section
            with Vertical(classes="log-section"):
                yield Label("📋 Execution Log", classes="section-header")
                self.log_panel = Static(classes="log-panel")
                yield self.log_panel
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application"""
        self.refresh_scripts_list()
        self.update_log(f"# BLUX Guard Scripts Explorer\n\nWelcome! Loaded {len(self.script_manager.get_scripts_list())} scripts.")
    
    def refresh_scripts_list(self):
        """Refresh the scripts list"""
        self.scripts_list.clear()
        scripts = self.script_manager.get_scripts_list()
        
        if not scripts:
            self.scripts_list.append(ListItem(Static("📭 No scripts found")))
            self.scripts_list.append(ListItem(Static("Click 'New Sample' to create example scripts")))
        else:
            for script in scripts:
                # Create rich display for script item
                display_text = self._format_script_display(script)
                item = ListItem(Static(display_text))
                item.script_data = script  # Attach script data to item
                self.scripts_list.append(item)
    
    def _format_script_display(self, script: Dict[str, Any]) -> str:
        """Format script information for display"""
        base_display = f"📄 {script['name']}"
        
        # Add security indicators
        if script["requires_root"]:
            base_display += " 🔴"
        elif script["security_level"] == "warning":
            base_display += " 🟡"
        else:
            base_display += " 🟢"
        
        # Add type indicator
        type_icons = {
            "Python Script": "🐍",
            "Shell Script": "🐚", 
            "Bash Script": "💻",
            "PowerShell": "🔷",
            "Batch File": "📟"
        }
        
        icon = type_icons.get(script["type"], "📝")
        base_display += f" {icon}"
        
        return base_display
    
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle script selection"""
        if hasattr(event.item, 'script_data'):
            self.selected_script = event.item.script_data
            self.update_log(f"**Selected:** {self.selected_script['name']}\n\n"
                          f"Type: {self.selected_script['type']}\n"
                          f"Size: {self.selected_script['size_kb']} KB\n"
                          f"Executable: {'✅ Yes' if self.selected_script['executable'] else '❌ No'}\n"
                          f"Security: {self.selected_script['security_level'].upper()}\n"
                          f"Modified: {self.selected_script['modified'].strftime('%Y-%m-%d %H:%M')}")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "btn_run":
            await self.action_run_script()
        elif button_id == "btn_view":
            await self.action_view_script()
        elif button_id == "btn_new":
            await self.action_new_script()
        elif button_id == "btn_refresh":
            self.action_refresh()
    
    async def action_run_script(self) -> None:
        """Run the selected script"""
        if not self.selected_script:
            self.update_log("❌ Please select a script first")
            return
        
        success = await self.script_manager.execute_script(
            self.selected_script, 
            self.update_log,
            require_auth=True
        )
        
        if success:
            self.notify("✅ Script executed successfully", severity="information")
        else:
            self.notify("❌ Script execution failed", severity="error")
    
    async def action_view_script(self) -> None:
        """View the selected script content"""
        if not self.selected_script:
            self.update_log("❌ Please select a script first")
            return
        
        content = self.script_manager.view_script_content(self.selected_script["path"])
        
        # Use rich syntax highlighting if available
        try:
            from rich.syntax import Syntax
            file_ext = self.selected_script["path"].suffix.lstrip('.')
            syntax = Syntax(content, file_ext or "text", line_numbers=True)
            self.update_log(syntax)
        except ImportError:
            # Fallback to plain text
            self.update_log(f"```\n{content}\n```")
    
    async def action_new_script(self) -> None:
        """Create a new sample script"""
        # For simplicity, create a Python sample
        success = self.script_manager.create_sample_script("python")
        
        if success:
            self.update_log("✅ Created sample Python security script")
            self.refresh_scripts_list()
            self.notify("📝 Sample script created", severity="information")
        else:
            self.update_log("❌ Failed to create sample script")
            self.notify("❌ Failed to create sample", severity="error")
    
    def action_refresh(self) -> None:
        """Refresh the scripts list"""
        self.refresh_scripts_list()
        self.update_log("🔄 Scripts list refreshed")
        self.notify("📜 List refreshed", severity="information")
    
    def update_log(self, content: str) -> None:
        """Update the log panel content"""
        # Keep log to reasonable size
        current_content = str(self.log_panel.renderable) if hasattr(self.log_panel.renderable, '__str__') else ""
        
        if isinstance(content, str) and content.startswith('#') or content.startswith('```'):
            # Replace content for new sections
            new_content = content
        else:
            # Append to existing content
            new_content = f"{current_content}\n\n{content}" if current_content else content
        
        # Limit log size
        if len(new_content) > 10000:
            new_content = new_content[-10000:]
        
        self.log_panel.update(Markdown(new_content))
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


# Basic console version for environments without Textual
class BasicScriptsView:
    """
    Basic scripts view for environments without Textual
    """
    
    def __init__(self):
        self.script_manager = ScriptManager()
    
    def display(self):
        """Display basic scripts interface"""
        scripts = self.script_manager.get_scripts_list()
        
        print("📜 BLUX Guard Scripts Explorer")
        print("=" * 50)
        
        if not scripts:
            print("No scripts found.")
            print("Creating sample script...")
            self.script_manager.create_sample_script("python")
            scripts = self.script_manager.get_scripts_list()
        
        for i, script in enumerate(scripts, 1):
            root_indicator = " 🔴" if script["requires_root"] else " 🟢"
            exec_indicator = " ✅" if script["executable"] else " ❌"
            print(f"{i}. {script['name']}{root_indicator}{exec_indicator}")
            print(f"   Type: {script['type']} | Size: {script['size_kb']} KB")
            print(f"   Security: {script['security_level'].upper()}")
            print()
        
        print("Commands: [r]un [v]iew [n]ew [q]uit")


def main():
    """Main entry point"""
    if not TEXTUAL_AVAILABLE:
        print("Textual not available - using basic scripts view")
        view = BasicScriptsView()
        view.display()
        return
    
    try:
        app = ScriptsViewApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start scripts view: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
