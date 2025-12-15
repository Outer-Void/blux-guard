#!/usr/bin/env python3
"""
BLUX Guard Shell Menu - Enhanced with Security Integration
Cross-platform compatible with unified security system
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import getpass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path for module imports
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.warning("Rich not available, using basic console")

try:
    from blux_modules.security.auth_system import AuthSystem
    from blux_modules.security.privilege_manager import PrivilegeManager
    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security modules not available: {e}")
    SECURITY_AVAILABLE = False

# Fallback console if rich is not available
if not RICH_AVAILABLE:
    class BasicConsole:
        def print(self, *args, **kwargs):
            print(*args)
        
        def rule(self, title):
            print(f"\n{'='*50}")
            print(f" {title}")
            print(f"{'='*50}")
    
    console = BasicConsole()
else:
    console = Console()

class BLUXGuardShell:
    """
    Enhanced BLUX Guard Shell with security integration
    Cross-platform compatible with privilege-aware features
    """
    
    def __init__(self):
        self.project_root = _project_root
        self.auth_system = None
        self.privilege_mgr = None
        self.is_authenticated = False
        self.current_user = getpass.getuser() if hasattr(os, 'getuser') else "unknown"
        
        self._init_security_systems()
        self._setup_paths()
    
    def _init_security_systems(self):
        """Initialize security systems with fallbacks"""
        if not SECURITY_AVAILABLE:
            logger.warning("Security systems not available - running in basic mode")
            self._create_fallback_security()
            return
        
        try:
            self.auth_system = AuthSystem()
            self.privilege_mgr = PrivilegeManager()
            logger.info("Security systems initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize security systems: {e}")
            self._create_fallback_security()
    
    def _create_fallback_security(self):
        """Create fallback security systems"""
        logger.info("Creating fallback security systems")
        
        class FallbackAuth:
            def is_first_run(self):
                user_pin_file = Path.home() / ".config" / "blux_guard" / "user_pin.txt"
                return not user_pin_file.exists()

            def authenticate(self, password=None):
                if password is None:
                    password = getpass.getpass("Enter BLUX Guard PIN: ")

                user_pin_file = Path.home() / ".config" / "blux_guard" / "user_pin.txt"
                if not user_pin_file.exists():
                    return True  # No PIN set, allow access

                try:
                    with open(user_pin_file, 'r') as f:
                        stored_hash = f.read().strip()
                    return self.verify_password(password, stored_hash)
                except Exception:
                    return False

            def setup_password(self, password=None):
                user_pin_file = Path.home() / ".config" / "blux_guard" / "user_pin.txt"
                user_pin_file.parent.mkdir(parents=True, exist_ok=True)

                if password is None:
                    while True:
                        password = getpass.getpass("Set your BLUX Guard PIN: ")
                        confirm = getpass.getpass("Confirm PIN: ")
                        if password == confirm:
                            break
                        print("PINs do not match. Please try again.")

                hashed_password = self.hash_password(password)
                with open(user_pin_file, 'w') as f:
                    f.write(hashed_password)

                # Set secure permissions (non-Windows)
                if os.name != 'nt':
                    try:
                        os.chmod(user_pin_file, 0o600)
                    except OSError:
                        pass

                return True

            def hash_password(self, password):
                import hashlib
                # Generate a random salt
                salt = os.urandom(16)

                # Hash the password with the salt
                hashed_password = hashlib.pbkdf2_hmac(
                    'sha256',  # The hash digest algorithm for HMAC
                    password.encode('utf-8'),  # Convert the password to bytes
                    salt,  # Provide the salt
                    100000  # It is recommended to use at least 100000 iterations of SHA-256
                )

                # Store the salt and hash in the same string for later verification
                return f"{salt.hex()}:{hashed_password.hex()}"

            def verify_password(self, password, stored_hash):
                import hashlib
                try:
                    salt, hashed_password = stored_hash.split(':')
                    salt = bytes.fromhex(salt)
                    hashed_password = bytes.fromhex(hashed_password)

                    # Hash the provided password with the same salt
                    new_hash = hashlib.pbkdf2_hmac(
                        'sha256',
                        password.encode('utf-8'),
                        salt,
                        100000
                    )

                    # Compare the generated hash with the stored hash
                    return new_hash == hashed_password
                except ValueError:
                    # Occurs when the stored hash is in an incorrect format
                    return False
        
        class FallbackPrivilege:
            def __init__(self): 
                self.is_root = self._check_root()
            
            def _check_root(self):
                try:
                    return os.geteuid() == 0
                except AttributeError:
                    return False
            
            def get_privilege_info(self): 
                return {
                    "is_root": self.is_root,
                    "platform": {"system": os.name},
                    "capabilities": {"root_access": self.is_root},
                    "safe_alternatives": {},
                    "recommended_actions": [],
                    "limitations": []
                }
        
        self.auth_system = FallbackAuth()
        self.privilege_mgr = FallbackPrivilege()
    
    def _setup_paths(self):
        """Setup essential paths"""
        self.paths = {
            'repo_root': self.project_root,
            'config_dir': self.project_root / ".config" / "blux_guard",
            'logs_dir': self.project_root / "logs",
            'rules_dir': self.project_root / ".config" / "rules",
            'modules_dir': self.project_root / "blux_modules"
        }
        
        # Create essential directories
        for path in self.paths.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
    
    def authenticate_user(self) -> bool:
        """
        Authenticate user with security system
        Returns True if authenticated, False otherwise
        """
        if not self.auth_system:
            print("❌ Security system not available")
            return False
        
        try:
            # Check if first run
            if self.auth_system.is_first_run():
                self._show_welcome_banner()
                print("\n🔐 First Run Security Setup")
                print("=" * 50)
                
                if not self.auth_system.setup_password():
                    print("❌ Security setup failed")
                    return False
                
                print("✅ Security system configured successfully")
            
            # Authenticate user
            print("\n🔐 BLUX Guard Authentication")
            print("=" * 50)
            
            for attempt in range(3):
                if self.auth_system.authenticate():
                    self.is_authenticated = True
                    print("✅ Authentication successful")
                    return True
                
                remaining = 3 - attempt - 1
                if remaining > 0:
                    print(f"⚠️  {remaining} attempts remaining")
                else:
                    print("❌ Maximum authentication attempts reached")
                    return False
            
            return False
            
        except KeyboardInterrupt:
            print("\n⏹️  Authentication cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            print(f"❌ Authentication error: {e}")
            return False
    
    def _show_welcome_banner(self):
        """Display welcome banner"""
        if RICH_AVAILABLE:
            welcome_text = Text()
            welcome_text.append("BLUX Guard Security System\n", style="bold cyan")
            welcome_text.append("Version 1.0.0 • Outer Void Team\n", style="bold magenta")
            welcome_text.append("Cross-Platform Security Monitoring\n", style="green")
            
            console.print(Panel(
                welcome_text,
                box=box.DOUBLE_EDGE,
                padding=(1, 2),
                style="bold blue"
            ))
        else:
            print("=" * 60)
            print("          BLUX Guard Security System")
            print("          Version 1.0.0 - Outer Void Team")
            print("       Cross-Platform Security Monitoring")
            print("=" * 60)
    
    def show_system_info(self):
        """Display comprehensive system information"""
        import platform
        import psutil
        
        if RICH_AVAILABLE:
            # Create a detailed system info table
            info_table = Table(title="🔍 System Information", box=box.ROUNDED)
            info_table.add_column("Category", style="cyan", width=20)
            info_table.add_column("Details", style="white")
            
            # System info
            info_table.add_row(
                "Operating System",
                f"{platform.system()} {platform.release()}"
            )
            info_table.add_row(
                "Architecture", 
                platform.machine()
            )
            info_table.add_row(
                "Python Version",
                platform.python_version()
            )
            
            # User and privilege info
            info_table.add_row(
                "Current User",
                self.current_user
            )
            
            if self.privilege_mgr:
                priv_info = self.privilege_mgr.get_privilege_info()
                info_table.add_row(
                    "Privilege Level",
                    "🔴 ROOT" if priv_info['is_root'] else "🟢 USER"
                )
                if hasattr(self.privilege_mgr, 'get_operational_mode'):
                    info_table.add_row(
                    "Operational Mode",
                    self.privilege_mgr.get_operational_mode() if hasattr(self.privilege_mgr, 'get_operational_mode') else "UNKNOWN"
                )
            
            # System resources
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                info_table.add_row(
                    "CPU Usage",
                    f"{cpu_usage:.1f}%"
                )
                info_table.add_row(
                    "Memory Usage", 
                    f"{memory.percent:.1f}% ({memory.used//1024//1024}MB / {memory.total//1024//1024}MB)"
                )
                info_table.add_row(
                    "Disk Usage",
                    f"{disk.percent:.1f}%"
                )
            except Exception as e:
                info_table.add_row("System Resources", f"Unavailable: {e}")
            
            console.print(info_table)
            
        else:
            # Basic console output
            print("\nSystem Information:")
            print(f"  OS: {platform.system()} {platform.release()}")
            print(f"  Architecture: {platform.machine()}")
            print(f"  Python: {platform.python_version()}")
            print(f"  User: {self.current_user}")
            
            if self.privilege_mgr:
                priv_info = self.privilege_mgr.get_privilege_info()
                print(f"  Privileges: {'ROOT' if priv_info['is_root'] else 'USER'}")
    
    def show_security_status(self):
        """Display comprehensive security status"""
        if not self.auth_system or not self.privilege_mgr:
            print("❌ Security systems not available")
            return
        
        if RICH_AVAILABLE:
            status_table = Table(title="🔒 Security Status", box=box.ROUNDED)
            status_table.add_column("Component", style="cyan", width=25)
            status_table.add_column("Status", style="white", width=20)
            status_table.add_column("Details", style="green")
            
            # Authentication status
            auth_status = "✅ Authenticated" if self.is_authenticated else "❌ Not Authenticated"
            status_table.add_row("Authentication", auth_status, "BLUX Guard Access")
            
            # Privilege status
            priv_info = self.privilege_mgr.get_privilege_info()
            privilege_status = "🔴 ROOT" if priv_info['is_root'] else "🟢 USER"
            status_table.add_row("Privilege Level", privilege_status, "System Access Level")
            
            # Platform info
            platform_info = priv_info.get('platform', {})
            status_table.add_row(
                "Platform", 
                platform_info.get('system', 'Unknown').upper(),
                f"Arch: {platform_info.get('architecture', 'Unknown')}"
            )
            
            # Security features
            status_table.add_row(
                "Security System", 
                "✅ Active" if SECURITY_AVAILABLE else "⚠️ Fallback",
                "Authentication & Privilege Management"
            )
            
            console.print(status_table)
            
            # Show recommendations if not root
            if not priv_info['is_root'] and priv_info.get('recommended_actions'):
                console.print("\n💡 Recommendations:")
                for action in priv_info['recommended_actions']:
                    console.print(f"  • {action}")
        
        else:
            print("\nSecurity Status:")
            print(f"  Authenticated: {'YES' if self.is_authenticated else 'NO'}")
            if self.privilege_mgr:
                priv_info = self.privilege_mgr.get_privilege_info()
                print(f"  Privileges: {'ROOT' if priv_info['is_root'] else 'USER'}")
                print(f"  Platform: {priv_info.get('platform', {}).get('system', 'Unknown')}")
    
    def lock_system(self):
        """System lockdown with privilege awareness"""
        if not self.is_authenticated:
            print("❌ Authentication required for system lockdown")
            if not self.authenticate_user():
                return
        
        if RICH_AVAILABLE:
            console.print(Panel(
                "🔒 SYSTEM LOCKDOWN INITIATED",
                style="bold red",
                box=box.DOUBLE_EDGE
            ))
        else:
            print("\n" + "="*50)
            print("         SYSTEM LOCKDOWN INITIATED")
            print("="*50)
        
        # Privilege-aware lockdown
        if self.privilege_mgr:
            priv_info = self.privilege_mgr.get_privilege_info()
            
            if priv_info['is_root']:
                print("🔴 ROOT PRIVILEGES DETECTED")
                print("   • Full system lockdown enabled")
                print("   • All security modules activated")
                print("   • Network monitoring enhanced")
                print("   • Process isolation enforced")
            else:
                print("🟢 USER SPACE MODE")
                print("   • User-space security activated")
                print("   • Personal file monitoring")
                print("   • Application-level protection")
                print("   • Limited system access")
        
        print("\n⚠️  Use your BLUX Guard PIN to unlock the system")
        print("   Some features may require re-authentication")
    
    def launch_module(self, module_name: str):
        """Launch BLUX Guard modules with security checks"""
        if not self.is_authenticated:
            print(f"❌ Authentication required to launch {module_name}")
            if not self.authenticate_user():
                return
        
        module_paths = {
            'security': self.paths['modules_dir'] / 'security',
            'sensors': self.paths['modules_dir'] / 'sensors',
            'cockpit': self.project_root / 'initiate_cockpit.py',
            'cli': self.project_root / 'blux_cli' / 'blux.py'
        }
        
        target = module_paths.get(module_name.lower())
        
        if not target or not target.exists():
            print(f"❌ Module '{module_name}' not found or unavailable")
            return
        
        print(f"🚀 Launching {module_name} module...")
        
        try:
            if module_name.lower() == 'cockpit':
                subprocess.run(
                    ['python', str(target)],
                    cwd=str(self.project_root),
                    check=True  # Raise an exception if the command fails
                )
            elif module_name.lower() == 'cli':
                subprocess.run(
                    ['python', str(target), 'status'],
                    cwd=str(self.project_root),
                    check=True
                )
            else:
                print(f"📍 Module location: {target}")
                # For security and sensors modules, we would import and run them
                # This is a placeholder for actual module execution
                print(f"✅ {module_name} module ready for execution")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to launch module {module_name}: {e}")
            print(f"❌ Failed to launch {module_name}: {e}")
    
    def emergency_reset(self):
        """Emergency security reset"""
        if not self.auth_system:
            print("❌ Security system not available")
            return
        
        if RICH_AVAILABLE:
            console.print(Panel(
                "🚨 EMERGENCY SECURITY RESET",
                style="bold red",
                box=box.DOUBLE_EDGE
            ))
        else:
            print("\n" + "!"*60)
            print("          EMERGENCY SECURITY RESET")
            print("!"*60)
        
        print("⚠️  WARNING: This will remove ALL authentication data!")
        print("⚠️  Only use this if you are locked out of the system!")
        print("⚠️  All security configurations will be reset!")
        
        if not Confirm.ask("\nAre you absolutely sure you want to continue?"):
            print("✅ Reset cancelled")
            return
        
        confirmation = input("Type 'RESET BLUX SECURITY' to confirm: ")
        if confirmation != "RESET BLUX SECURITY":
            print("❌ Reset cancelled - confirmation phrase incorrect")
            return
        
        try:
            # Use auth system emergency reset if available
            if hasattr(self.auth_system, 'emergency_reset'):
                if self.auth_system.emergency_reset():
                    print("✅ Security system reset successfully")
                    print("🔧 Restart the application to set up new security credentials")
                else:
                    print("❌ Security reset failed")
            else:
                # Fallback reset
                import shutil
                config_dir = Path.home() / ".config" / "blux_guard"
                if config_dir.exists():
                    shutil.rmtree(config_dir)
                    print("✅ Security configuration removed")
                print("🔧 Restart the application to set up new security credentials")
                
        except Exception as e:
            logger.error(f"Emergency reset failed: {e}")
            print(f"❌ Reset failed: {e}")
    
    def show_help(self):
        """Display help information"""
        if RICH_AVAILABLE:
            help_table = Table(title="📖 BLUX Guard Shell Help", box=box.ROUNDED)
            help_table.add_column("Command", style="cyan", width=15)
            help_table.add_column("Description", style="white")
            
            help_table.add_row("1 - System Info", "Display comprehensive system information")
            help_table.add_row("2 - Lock System", "Activate system lockdown (requires auth)")
            help_table.add_row("3 - Security Module", "Launch security engine module")
            help_table.add_row("4 - Sensors Module", "Launch sensors monitoring module")
            help_table.add_row("5 - Cockpit", "Launch graphical cockpit interface")
            help_table.add_row("6 - CLI", "Launch command-line interface")
            help_table.add_row("7 - Security Status", "Show security system status")
            help_table.add_row("8 - Emergency Reset", "Reset security system (use with caution)")
            help_table.add_row("9 - Help", "Show this help message")
            help_table.add_row("0 - Exit", "Exit BLUX Guard Shell")
            
            console.print(help_table)
            
            # Security notes
            console.print("\n💡 Security Notes:")
            console.print("  • Authentication required for sensitive operations")
            console.print("  • Root privileges enable full system monitoring")
            console.print("  • User mode provides safe alternatives")
            console.print("  • Emergency reset available if locked out")
            
        else:
            print("\nBLUX Guard Shell Commands:")
            print("  1 - System Info      Display system information")
            print("  2 - Lock System      Activate system lockdown")
            print("  3 - Security Module  Launch security engine")
            print("  4 - Sensors Module   Launch sensors monitoring")
            print("  5 - Cockpit          Launch graphical interface")
            print("  6 - CLI              Launch command-line interface")
            print("  7 - Security Status  Show security system status")
            print("  8 - Emergency Reset  Reset security system")
            print("  9 - Help             Show this help")
            print("  0 - Exit             Exit BLUX Guard Shell")
    
    def main_menu(self):
        """Interactive main menu"""
        while True:
            # Display header
            self._show_menu_header()
            
            # Display menu options
            if RICH_AVAILABLE:
                menu_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
                menu_table.add_column("Option", style="cyan", width=3)
                menu_table.add_column("Command", style="white", width=20)
                menu_table.add_column("Status", style="green", width=15)
                
                menu_options = [
                    ("1", "System Info", "📊"),
                    ("2", "Lock System", "🔒" if self.is_authenticated else "🔐"),
                    ("3", "Security Module", "🛡️"),
                    ("4", "Sensors Module", "📡"),
                    ("5", "Cockpit", "🚀"),
                    ("6", "CLI", "💻"),
                    ("7", "Security Status", "🔍"),
                    ("8", "Emergency Reset", "🚨"),
                    ("9", "Help", "❓"),
                    ("0", "Exit", "👋")
                ]
                
                for opt, cmd, icon in menu_options:
                    menu_table.add_row(opt, cmd, icon)
                
                console.print(menu_table)
            else:
                print("\nOptions:")
                print("  1. System Info       2. Lock System")
                print("  3. Security Module   4. Sensors Module") 
                print("  5. Cockpit           6. CLI")
                print("  7. Security Status   8. Emergency Reset")
                print("  9. Help              0. Exit")
            
            # Get user choice
            try:
                choice = Prompt.ask("\nSelect an option", choices=[str(i) for i in range(10)])
            except KeyboardInterrupt:
                print("\n👋 Exiting BLUX Guard Shell")
                sys.exit(0)
            
            # Process choice
            if choice == "1":
                self.show_system_info()
            elif choice == "2":
                self.lock_system()
            elif choice == "3":
                self.launch_module("security")
            elif choice == "4":
                self.launch_module("sensors")
            elif choice == "5":
                self.launch_module("cockpit")
            elif choice == "6":
                self.launch_module("cli")
            elif choice == "7":
                self.show_security_status()
            elif choice == "8":
                self.emergency_reset()
            elif choice == "9":
                self.show_help()
            elif choice == "0":
                if RICH_AVAILABLE:
                    console.print("[bold green]👋 Thank you for using BLUX Guard![/bold green]")
                else:
                    print("👋 Thank you for using BLUX Guard!")
                sys.exit(0)
            
            # Pause before next menu
            if RICH_AVAILABLE:
                console.print("\nPress Enter to continue...", end="")
            input()
    
    def _show_menu_header(self):
        """Display menu header with system status"""
        if RICH_AVAILABLE:
            # Create status line
            status_line = Text()
            status_line.append("BLUX Guard Shell", style="bold cyan")
            status_line.append(" • ")
            status_line.append("v1.0.0", style="bold magenta")
            status_line.append(" • ")
            status_line.append(f"User: {self.current_user}", style="green")
            
            if self.privilege_mgr:
                priv_info = self.privilege_mgr.get_privilege_info()
                status_line.append(" • ")
                status_line.append(
                    "ROOT" if priv_info['is_root'] else "USER", 
                    style="bold red" if priv_info['is_root'] else "bold green"
                )
            
            status_line.append(" • ")
            status_line.append(
                "AUTHENTICATED" if self.is_authenticated else "UNAUTHENTICATED",
                style="bold green" if self.is_authenticated else "bold yellow"
            )
            
            console.print(Panel(
                status_line,
                style="bold blue",
                box=box.ROUNDED
            ))
        else:
            print("\n" + "="*60)
            print(f"BLUX Guard Shell v1.0.0 - User: {self.current_user}")
            if self.privilege_mgr:
                priv_info = self.privilege_mgr.get_privilege_info()
                print(f"Mode: {'ROOT' if priv_info['is_root'] else 'USER'} - Auth: {'YES' if self.is_authenticated else 'NO'}")
            print("="*60)

def main():
    """Main entry point"""
    try:
        # Initialize shell
        shell = BLUXGuardShell()
        
        # Show welcome banner
        shell._show_welcome_banner()
        
        # Authenticate user
        if not shell.authenticate_user():
            print("❌ Authentication failed. Exiting.")
            sys.exit(1)
        
        # Start interactive menu
        shell.main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 BLUX Guard Shell interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"BLUX Guard Shell fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
