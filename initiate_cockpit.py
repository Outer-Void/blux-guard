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
import getpass  # Add this import at the top

# Textual imports
try:
    from textual.app import App
    from textual.widgets import Header, Footer, Static
    from textual.containers import Container
    from textual.reactive import reactive
    from datetime import datetime
except ImportError as e:
    print("Required dependencies missing. Install with: pip install textual rich")
    sys.exit(1)

# Configure logging
config_dir = Path.home() / '.config' / 'blux_guard'
config_dir.mkdir(parents=True, exist_ok=True)

log_file = config_dir / 'blux_guard.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=str(log_file)
)
logger = logging.getLogger(__name__)

# Add correct module paths
module_path = Path(__file__).parent / 'blux_modules'
sys.path.insert(0, str(module_path))

# BLUX Guard imports with better error handling
SENSORS_AVAILABLE = DECISIONS_AVAILABLE = ANTITAMPER_AVAILABLE = CONTAINMENT_AVAILABLE = False
auth_system = None
privilege_mgr = None

try:
    # Try to import security modules
    from blux_modules.security.auth_system import AuthSystem
    SENSORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Auth system not available: {e}")

try:
    from blux_modules.security.privilege_manager import PrivilegeManager
    DECISIONS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Privilege manager not available: {e}")

# Create fallbacks if imports failed
if auth_system is None:
    class AuthSystem:
        def authenticate(self): 
            return True
        def get_security_status(self): 
            return {
                'password_set': False, 
                'failed_attempts': 0, 
                'max_attempts': 3, 
                'locked_out': False,
                'is_root': False,
                'auth_method': 'fallback'
            }
        def setup_password(self): 
            return True
        def change_password(self): 
            print("Password change not available (fallback mode).")
        def emergency_reset(self):
            print("Emergency reset not available (fallback mode).")
    
    auth_system = AuthSystem()

if privilege_mgr is None:
    class PrivilegeManager:
        def __init__(self):
            self.is_root = False
            self.platform_info = {
                'is_windows': platform.system() == 'Windows',
                'is_android': False,
            }
            
        def get_privilege_info(self): 
            return {
                'is_root': False, 
                'platform': {
                    'system': platform.system(), 
                    'architecture': platform.machine()
                }, 
                'safe_alternatives': {},
                'recommended_actions': ['Run in fallback mode']
            }
        def get_operational_mode(self): 
            return "User Space (Fallback)"
    
    privilege_mgr = PrivilegeManager()

# Security Configuration
CONFIG_DIR = Path.home() / '.config' / 'blux_guard'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PASSWORD_FILE = CONFIG_DIR / 'lock.hash'

# Fixed hashing function
def hash_password(password: str, salt: bytes = None) -> tuple:
    """Hashes the password using a secure method."""
    if salt is None:
        salt = secrets.token_bytes(16)

    # Use PBKDF2 for reliable hashing
    hasher = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(hasher).decode('utf-8'), base64.b64encode(salt).decode('utf-8')

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verifies the password against the hashed password and salt."""
    salt_bytes = base64.b64decode(salt)
    test_hash, _ = hash_password(password, salt_bytes)
    return test_hash == hashed_password

def save_password(hashed_password: str, salt: str):
    """Saves the hashed password and salt to a file."""
    try:
        with open(PASSWORD_FILE, 'w') as f:
            json.dump({'hashed_password': hashed_password, 'salt': salt}, f)
        os.chmod(PASSWORD_FILE, 0o600)
        print("Password saved securely.")
    except Exception as e:
        print(f"Error saving password: {e}")

def load_password():
    """Loads the hashed password and salt from the file."""
    if not PASSWORD_FILE.exists():
        return None
    try:
        with open(PASSWORD_FILE, 'r') as f:
            data = json.load(f)
        return data['hashed_password'], data['salt']
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error loading password: {e}")
        return None

def prompt_for_password() -> str:
    """Prompts the user for a password."""
    while True:
        password = getpass.getpass("Enter password: ")
        if password:
            return password
        print("Password cannot be empty.")

def first_run_setup() -> bool:
    """Handles the first-run setup."""
    print("First run detected. Setting up password...")
    password = prompt_for_password()
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match. Setup failed.")
        return False
    
    hashed_password, salt = hash_password(password)
    save_password(hashed_password, salt)
    return True

class StatusPanel(Static):
    """A panel for displaying status information"""
    
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = ""

    def update_content(self, content: str):
        self.content = content
        self.update(f"[bold]{self.title}[/bold]\n{content}")

class BLUXGuardUltraShell(App):
    """BLUX Guard Ultra Cockpit with integrated security system"""

    # Reactive attributes
    sensor_status = reactive({})
    decision_logs = reactive([])
    anti_tamper_status = reactive({})
    security_status = reactive({})

    async def on_load(self):
        """Initialize security on app load"""
        await self.initialize_security()

    async def initialize_security(self):
        """Initialize security system"""
        logger.info("Initializing security system...")

        # Password Check
        stored_creds = load_password()

        if stored_creds is None:
            if not first_run_setup():
                print("Security setup failed. Exiting.")
                sys.exit(1)
            stored_creds = load_password()
            if stored_creds is None:
                print("Failed to setup password. Exiting.")
                sys.exit(1)

        hashed_password, salt = stored_creds

        # Authentication loop
        max_attempts = 3
        authenticated = False
        for attempt in range(max_attempts):
            password = prompt_for_password()
            if verify_password(password, hashed_password, salt):
                print("Authentication successful.")
                authenticated = True
                break
            else:
                remaining_attempts = max_attempts - attempt - 1
                if remaining_attempts > 0:
                    print(f"Authentication failed. {remaining_attempts} attempts remaining.")
                else:
                    print("Too many failed attempts. Exiting.")
                    sys.exit(1)
        
        if not authenticated:
            print("Authentication failed. Exiting.")
            sys.exit(1)

        # Initialize security systems
        global auth_system, privilege_mgr
        try:
            # Re-initialize with actual implementations if available
            from blux_modules.security.auth_system import AuthSystem
            from blux_modules.security.privilege_manager import PrivilegeManager
            auth_system = AuthSystem()
            privilege_mgr = PrivilegeManager()
        except ImportError:
            # Keep using fallbacks
            pass

        # Display system information
        priv_info = privilege_mgr.get_privilege_info()
        print(f"BLUX Guard Ultra Cockpit v1.0.0")
        print(f"Platform: {priv_info['platform']['system']}")
        print(f"Architecture: {priv_info['platform']['architecture']}")
        print(f"Root Access: {priv_info.get('is_root', False)}")
        print(f"Operational Mode: {privilege_mgr.get_operational_mode()}")

        # Load security status
        self.security_status = auth_system.get_security_status()

    def compose(self):
        """Create the UI layout"""
        yield Header()
        yield Container(
            StatusPanel("Security Status", id="security-panel"),
            StatusPanel("Sensors", id="sensors-panel"), 
            StatusPanel("Decisions", id="decisions-panel"),
            StatusPanel("Anti-Tamper", id="anti-tamper-panel"),
        )
        yield Footer()

    async def on_mount(self):
        """Setup initial UI state"""
        # Start background updates
        self.set_interval(2, self.update_panels)
        await self.update_panels()

    async def update_panels(self):
        """Update all status panels"""
        try:
            # Security Status
            security_text = self._format_security_status()
            self.query_one("#security-panel", StatusPanel).update_content(security_text)

            # Sensors
            sensors_text = self._format_sensor_status()
            self.query_one("#sensors-panel", StatusPanel).update_content(sensors_text)

            # Decisions
            decisions_text = self._format_decisions_status()
            self.query_one("#decisions-panel", StatusPanel).update_content(decisions_text)

            # Anti-Tamper
            anti_tamper_text = self._format_anti_tamper_status()
            self.query_one("#anti-tamper-panel", StatusPanel).update_content(anti_tamper_text)

        except Exception as e:
            logger.error(f"Panel update failed: {e}")

    def _format_security_status(self) -> str:
        """Format security status for display"""
        status = self.security_status
        root_icon = "🔴" if status.get('is_root', False) else "🟢"
        locked_icon = "🔴" if status.get('locked_out', False) else "🟢"
        password_icon = "🟢" if status.get('password_set', False) else "🔴"

        return f"""{root_icon} Root: {status.get('is_root', False)}
{password_icon} Password: Set
{locked_icon} Locked: {status.get('locked_out', False)}
Attempts: {status.get('failed_attempts', 0)}/{status.get('max_attempts', 5)}
Method: {status.get('auth_method', 'unknown')}"""

    def _format_sensor_status(self) -> str:
        """Format sensor status"""
        if not self.sensor_status:
            return "No sensor data\nAvailable: " + str(SENSORS_AVAILABLE)
        
        lines = []
        for key, value in self.sensor_status.items():
            if isinstance(value, (int, float)):
                if value > 80:
                    lines.append(f"🔴 {key}: {value}")
                elif value > 50:
                    lines.append(f"🟡 {key}: {value}")
                else:
                    lines.append(f"🟢 {key}: {value}")
            else:
                status_icon = "🔴" if value else "🟢"
                lines.append(f"{status_icon} {key}: {value}")
        
        return "\n".join(lines)

    def _format_decisions_status(self) -> str:
        """Format decisions status"""
        if not self.decision_logs:
            return "No decision logs\nAvailable: " + str(DECISIONS_AVAILABLE)
        
        recent_logs = self.decision_logs[-5:]  # Show last 5 logs
        return "\n".join(str(log) for log in recent_logs)

    def _format_anti_tamper_status(self) -> str:
        """Format anti-tamper status"""
        if not self.anti_tamper_status:
            return "No anti-tamper data\nAvailable: " + str(ANTITAMPER_AVAILABLE)
        
        lines = []
        for key, value in self.anti_tamper_status.items():
            status_icon = "🔴" if value else "🟢"
            lines.append(f"{status_icon} {key}: {'ALERT' if value else 'OK'}")
        
        return "\n".join(lines)

    async def on_key(self, event):
        """Handle keyboard input"""
        key = event.key.lower()
        
        if key == "q":
            await self.action_quit()
        elif key == "s":
            print("Security status refreshed")
            await self.update_panels()
        elif key == "r":
            print("Refresh triggered")
            await self.update_panels()

def main():
    """Main entry point"""
    print("BLUX Guard Ultra Cockpit - Security System Initializing...")

    try:
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
