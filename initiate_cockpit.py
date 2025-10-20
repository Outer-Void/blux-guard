import os
import sys
import asyncio
import platform
import logging
from pathlib import Path
import hashlib
import secrets
import base64
import json

# Textual imports (moved up for earlier error handling)
try:
    from textual.app import App
    from textual.widgets import Header, Footer, ScrollView, Panel, Input
    from textual.reactive import Reactive
    from datetime import datetime
    from rich.markdown import Markdown
except ImportError as e:
    print("Required dependencies missing. Install with: pip install textual rich")
    sys.exit(1)

# Configure logging
config_dir = Path.home() / '.config' / 'blux_guard'
config_dir.mkdir(parents=True, exist_ok=True)  # Ensure config directory exists

log_file = config_dir / 'blux_guard.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=str(log_file)  # Log to file
)
logger = logging.getLogger(__name__)

# Add blux_modules to path
module_path = Path(__file__).parent / 'blux_modules'
sys.path.insert(0, str(module_path))


# BLUX Guard imports with error handling
try:
    from blux_modules.security.auth_system import AuthSystem  # Adjusted import
    from blux_modules.security.privilege_manager import PrivilegeManager  # Adjusted import

    try:
        from blux_modules.security.sensors_manager import get_sensor_status

        SENSORS_AVAILABLE = True
    except ImportError:
        SENSORS_AVAILABLE = False
        logger.warning("Sensors manager not available")

    try:
        from blux_modules.security.trip_engine import get_decision_logs

        DECISIONS_AVAILABLE = True
    except ImportError:
        DECISIONS_AVAILABLE = False
        logger.warning("Trip engine not available")

    try:
        from blux_modules.security.anti_tamper_engine import get_anti_tamper_status

        ANTITAMPER_AVAILABLE = True
    except ImportError:
        ANTITAMPER_AVAILABLE = False
        logger.warning("Anti-tamper engine not available")

    try:
        from blux_modules.security.contain_engine import execute_containment

        CONTAINMENT_AVAILABLE = True
    except ImportError:
        CONTAINMENT_AVAILABLE = False
        logger.warning("Containment engine not available")

except ImportError as e:
    logger.error(f"BLUX Guard imports failed: {e}")
    print("Some BLUX Guard features may be unavailable.")
    # Create minimal fallbacks
    class AuthSystem:  # Fallback AuthSystem
        def authenticate(self): return True  # Dummy auth
        def get_security_status(self): return {'password_set': False, 'failed_attempts': 0, 'max_attempts': 3, 'locked_out': False}
        def setup_password(self): return True
        def change_password(self): print("Password change not available (fallback mode).")
    class PrivilegeManager:  # Fallback
        def get_privilege_info(self): return {'is_root': False, 'platform': {'system': platform.system(), 'architecture': platform.machine()}, 'safe_alternatives': {}}
        def get_operational_mode(self): return "User Space (Fallback)"

    SENSORS_AVAILABLE = DECISIONS_AVAILABLE = ANTITAMPER_AVAILABLE = CONTAINMENT_AVAILABLE = False

# --- Security Configuration ---
CONFIG_DIR = Path.home() / '.config' / 'blux_guard'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PASSWORD_FILE = CONFIG_DIR / 'lock.hash'

# --- Hashing function (Argon2) ---
def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """Hashes the password using Argon2."""
    if salt is None:
        salt = secrets.token_bytes(16)  # Generate a new salt if none is provided

    # Using hashlib's Argon2 implementation
    hashed_password = hashlib.argon2id_hash(password.encode('utf-8'), salt=salt)

    return hashed_password, base64.b64encode(salt).decode('utf-8')

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verifies the password against the hashed password and salt."""
    salt_bytes = base64.b64decode(salt)
    try:
        hashlib.argon2.verify(hashed_password, password.encode('utf-8'), salt=salt_bytes)  # type: ignore
        return True
    except Exception as e:
        print(f"Verification error: {e}")
        return False



def save_password(hashed_password: str, salt: str):
    """Saves the hashed password and salt to a file."""
    try:
        with open(PASSWORD_FILE, 'w') as f:  # Open file for writing
            json.dump({'hashed_password': hashed_password, 'salt': salt}, f)
        os.chmod(PASSWORD_FILE, 0o600)  # Restrict file permissions
        print("Password saved securely.")
    except Exception as e:
        print(f"Error saving password: {e}")


def load_password() -> tuple[str, str] | None:
    """Loads the hashed password and salt from the file."""
    if not PASSWORD_FILE.exists():
        return None
    try:
        with open(PASSWORD_FILE, 'r') as f:
            data = json.load(f)
        return data['hashed_password'], data['salt']
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None

def prompt_for_password() -> str:
    """Prompts the user for a password."""
    import getpass
    while True:
        password = getpass.getpass("Enter password: ")
        if password:
            return password
        print("Password cannot be empty.")

def first_run_setup() -> bool:
    """Handles the first-run setup, prompting for a password and saving it."""
    print("First run detected. Setting up password...")
    password = prompt_for_password()
    hashed_password, salt = hash_password(password)
    save_password(hashed_password, salt)
    return True

# --- End Security Configuration ---

# Initialize security systems - Deferred until after password setup
# auth_system = AuthSystem() # Initialize after password is set
# privilege_mgr = PrivilegeManager() # Initialize after password is set

# --- Hotkeys mapping ---
HOTKEY_COMMANDS = {
    "r": ("Run Containment", lambda: execute_containment() if 'execute_containment' in globals() else None),
    "s": ("Security Status", lambda: auth_system.get_security_status() if 'auth_system' in globals() else None),  # Check if auth_system is defined
    "p": ("Privilege Info", lambda: privilege_mgr.get_privilege_info() if 'privilege_mgr' in globals() else None),  # Check if privilege_mgr is defined
}


class BLUXGuardUltraShell(App):
    """BLUX Guard Ultra Cockpit with integrated security system"""

    # Reactive attributes for UI updates
    sensor_status: Reactive[dict] = Reactive({})
    decision_logs: Reactive[list] = Reactive([])
    anti_tamper_status: Reactive[dict] = Reactive({})
    security_status: Reactive[dict] = Reactive({})
    shell_mode: Reactive[bool] = Reactive(False)

    async def on_load(self):
        """Initialize security on app load"""
        await self.initialize_security()

    async def initialize_security(self):
        """Initialize security system with cross-platform compatibility"""
        logger.info("Initializing security system...")

        # --- Password Check ---
        hashed_password, salt = load_password()

        if hashed_password is None or salt is None:
            if not first_run_setup():
                print("Security setup failed. Exiting.")
                sys.exit(1)
        else:
            # Authentication loop
            max_attempts = 3
            for attempt in range(max_attempts):
                password = prompt_for_password()
                if verify_password(password, hashed_password, salt):
                    print("Authentication successful.")
                    break  # Exit loop on success
                else:
                    remaining_attempts = max_attempts - attempt - 1
                    if remaining_attempts > 0:
                        print(f"Authentication failed. {remaining_attempts} attempts remaining.")
                    else:
                        print("Too many failed attempts. Exiting.")
                        sys.exit(1)  # Exit after too many attempts
            else:  # This 'else' belongs to the 'for' loop
                print("Authentication failed. Exiting.")
                sys.exit(1)

        # --- End Password Check ---

        # Initialize security systems (now that password is verified)
        global auth_system, privilege_mgr  # Use globals to update the module-level variables
        auth_system = AuthSystem()
        privilege_mgr = PrivilegeManager()
        
        # Display system information
        priv_info = privilege_mgr.get_privilege_info()
        print(f"BLUX Guard Ultra Cockpit v1.0.0")
        print(f"Platform: {priv_info['platform']['system']}")
        print(f"Architecture: {priv_info['platform']['architecture']}")
        print(f"Root Access: {priv_info['is_root']}")
        print(f"Operational Mode: {privilege_mgr.get_operational_mode()}")

        # Show safe alternatives if not root
        if not priv_info['is_root']:
            print("\nRunning in USER SPACE mode:")
            for feature, alternative in priv_info['safe_alternatives'].items():
                print(f"  {feature}: {alternative}")

        # Load security status
        if 'auth_system' in globals():
            self.security_status = auth_system.get_security_status()  # Get status if auth_system is available

        # Display privilege information
        if 'privilege_mgr' in globals():
            for action in priv_info['recommended_actions']:
                print(f"Note: {action}")
    # --- No longer using authenticate_user function ---

    async def on_mount(self):
        """Setup UI layout"""
        try:
            # Layout
            await self.view.dock(Header(), edge="top")
            await self.view.dock(Footer(), edge="bottom")

            self.sensors_view = ScrollView()
            self.decisions_view = ScrollView()
            self.anti_tamper_view = ScrollView()
            self.security_view = ScrollView()

            await self.view.dock(self.sensors_view, edge="left", size=25)
            await self.view.dock(self.decisions_view, edge="left", size=40)
            await self.view.dock(self.anti_tamper_view, edge="right", size=20)
            await self.view.dock(self.security_view, edge="right", size=15)

            # Background update
            self.set_interval(2, self.update_views)

        except Exception as e:
            logger.error(f"UI mounting failed: {e}")
            raise

    async def update_views(self):
        """Update all dashboard views with error handling"""
        try:
            # Security Status
            security_text = self._format_security_status()
            await self.security_view.update(security_text)

            # Sensors (with error handling)
            if SENSORS_AVAILABLE:
                try:
                    self.sensor_status = get_sensor_status()
                    await self.sensors_view.update(self._format_sensor_text(self.sensor_status))
                except Exception as e:
                    await self.sensors_view.update(f"Sensor Error:\n{str(e)}")
            else:
                await self.sensors_view.update("Sensors: Not Available")

            # Decisions (with error handling)
            if DECISIONS_AVAILABLE:
                try:
                    self.decision_logs = get_decision_logs()[-30:]
                    dec_text = "\n".join(f"[yellow]{log}[/yellow]" for log in self.decision_logs)
                    await self.decisions_view.update(Markdown(dec_text))
                except Exception as e:
                    await self.decisions_view.update(f"Decisions Error:\n{str(e)}")
            else:
                await self.decisions_view.update("Decisions: Not Available")

            # Anti-Tamper (with error handling)
            if ANTITAMPER_AVAILABLE:
                try:
                    self.anti_tamper_status = get_anti_tamper_status()
                    anti_text = self._format_anti_tamper_status(self.anti_tamper_status)
                    await self.anti_tamper_view.update(anti_text)
                except Exception as e:
                    await self.anti_tamper_view.update(f"Anti-Tamper Error:\n{str(e)}")
            else:
                await self.anti_tamper_view.update("Anti-Tamper: Not Available")

            # Update footer with hotkeys
            await self.update_footer()

        except Exception as e:
            logger.error(f"View update failed: {e}")

    def _format_security_status(self) -> str:
        """Format security status for display"""
        status = self.security_status
        root_icon = "🔴" if status.get('is_root', False) else "🟢"
        locked_icon = "🔴" if status.get('locked_out', False) else "🟢"
        password_icon = "🟢" if status.get('password_set', False) else "🔴"

        return f"""Security Status:
{root_icon} Root: {status.get('is_root', False)}
{password_icon} Password: Set
{locked_icon} Locked: {status.get('locked_out', False)}
Attempts: {status.get('failed_attempts', 0)}/{status.get('max_attempts', 5)}
Method: {status.get('auth_method', 'unknown')}"""

    def _format_sensor_text(self, sensor_dict: dict) -> str:
        """Format sensor data with color coding"""

        def color_status(value, thresholds=(50, 75, 90)):
            low, mid, high = thresholds
            try:
                val = float(value)
                if val >= high:
                    return f"[red]{val}[/red]"
                elif val >= mid:
                    return f"[yellow]{val}[/yellow]"
                else:
                    return f"[green]{val}[/green]"
            except:
                return "[green]OK[/green]" if not value else "[red]ALERT[/red]"

        if not sensor_dict:
            return "No sensor data"

        return "\n".join(f"{k}: {color_status(v)}" for k, v in sensor_dict.items())

    def _format_anti_tamper_status(self, status_dict: dict) -> str:
        """Format anti-tamper status"""
        if not status_dict:
            return "No anti-tamper data"

        lines = []
        for k, v in status_dict.items():
            status_icon = "🔴" if v else "🟢"
            lines.append(f"{status_icon} {k}: {'ALERT' if v else 'OK'}")

        return "\n".join(lines)

    async def update_footer(self):
        """Update footer with current hotkeys"""
        footer_text = " | ".join(f"{k.upper()}: {v[0]}" for k, v in HOTKEY_COMMANDS.items())
        footer_text += " | C: Shell | A: Auth | Q: Quit"

        # Add privilege indicator
        priv_info = privilege_mgr.get_privilege_info()
        root_indicator = "ROOT" if priv_info['is_root'] else "USER"
        footer_text = f"[{root_indicator}] {footer_text}"

        try:
            await self.view.footer.update(footer_text)
        except Exception as e:
            logger.error(f"Footer update failed: {e}")

    async def on_key(self, event):
        """Handle keyboard input"""
        key = event.key.lower()

        if self.shell_mode:
            return  # Disable hotkeys in shell mode

        try:
            if key in HOTKEY_COMMANDS:
                name, func = HOTKEY_COMMANDS[key]
                self.decision_logs.append(f"{datetime.now().strftime('%H:%M:%S')} | HOTKEY: {name}")
                result = func()
                if result:
                    print(f"Executed: {name}")

            elif key == "q":
                await self.action_quit()

            elif key == "c":
                await self.enter_shell_mode()

            elif key == "a":
                await self.show_auth_menu()

        except Exception as e:
            logger.error(f"Key handler error: {e}")

    async def show_auth_menu(self):
        """Show authentication management menu"""
        print("\nAuthentication Menu:")
        print("1. Change Password")
        print("2. Security Status")
        print("3. Emergency Reset (Dangerous!)")
        print("4. Back")

        try:
            choice = input("Select option: ").strip()
            if choice == "1":
                auth_system.change_password()
            elif choice == "2":
                status = auth_system.get_security_status()
                print(f"\nSecurity Status:")
                print(f"Password Set: {status['password_set']}")
                print(f"Failed Attempts: {status['failed_attempts']}/{status['max_attempts']}")
                print(f"Locked Out: {status['locked_out']}")
                print(f"Auth Method: {status['auth_method']}")
            elif choice == "3":
                print("\n⚠️  EMERGENCY RESET WILL REMOVE ALL AUTHENTICATION DATA!")
                confirm = input("Type 'CONFIRM RESET' to proceed: ")
                if confirm == "CONFIRM RESET":
                    auth_system.emergency_reset()
                else:
                    print("Reset cancelled.")
        except (KeyboardInterrupt, EOFError):
            print("\nMenu cancelled.")

    async def enter_shell_mode(self):
        """Launch embedded non-blocking command shell"""
        if not privilege_mgr.is_root:
            print("Shell mode limited in user space for security")

        self.shell_mode = True
        shell_input = Input(placeholder="Type command (exit to return)...")
        shell_output = ScrollView()

        try:
            await self.view.dock(shell_output, edge="bottom", size=12)
            await self.view.dock(shell_input, edge="bottom", size=3)

            async def run_command(cmd):
                """Execute shell command safely"""
                try:
                    # Security check - prevent dangerous commands in non-root
                    dangerous_cmds = ['rm -rf', 'dd if=', 'mkfs', ':(){:|:&};:']
                    if not privilege_mgr.is_root and any(danger in cmd for danger in dangerous_cmds):
                        await shell_output.update("Command blocked for security in user mode")
                        return

                    # Determine shell based on platform
                    if privilege_mgr.platform_info['is_windows']:
                        shell_cmd = ["cmd", "/c", cmd]
                    elif privilege_mgr.platform_info['is_android']:
                        shell_cmd = ["/data/data/com.termux/files/usr/bin/bash", "-c", cmd]
                    else:
                        shell_cmd = ["/bin/bash", "-c", cmd]

                    proc = await asyncio.create_subprocess_exec(
                        *shell_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    output_text = stdout.decode() + stderr.decode()
                    await shell_output.update(output_text[:2000])  # Limit output

                except Exception as e:
                    await shell_output.update(f"Command error: {e}")

            async def handle_input():
                while True:
                    cmd = await shell_input.get_value()
                    if cmd.strip().lower() == "exit":
                        await shell_input.remove()
                        await shell_output.remove()
                        self.shell_mode = False
                        break
                    elif cmd.strip():
                        await run_command(cmd)
                        shell_input.value = ""

            asyncio.create_task(handle_input())

        except Exception as e:
            logger.error(f"Shell mode failed: {e}")
            self.shell_mode = False


def main():
    """Main entry point with security initialization"""
    print("BLUX Guard Ultra Cockpit - Security System Initializing...")

    try:
        # Initialize and run the app
        app = BLUXGuardUltraShell()
        app.run()
    except KeyboardInterrupt:
        print("\nBLUX Guard shutdown by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
