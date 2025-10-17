#!/usr/bin/env python3
"""
BLUX Guard CLI Launcher - Multi-environment compatible
Enhanced with unified security system
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import subprocess
import signal
import time
import json
import platform
import logging
from pathlib import Path

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

# Import security integration
try:
    from blux_cli.security_integration import SecurityIntegration
    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security integration not available: {e}")
    SECURITY_AVAILABLE = False

# ----------------------
# Environment Detection
# ----------------------
def detect_environment():
    """Detect the current operating environment"""
    system = platform.system().lower()
    
    # Check for Android/Termux
    if hasattr(os, 'getppid') and 'termux' in os.environ.get('PREFIX', '').lower():
        return "termux"
    elif os.path.exists('/system/bin/adb') or os.path.exists('/system/app'):
        return "android"
    # Check for WSL
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

ENVIRONMENT = detect_environment()

# ----------------------
# Path Configuration
# ----------------------
def setup_paths():
    """Setup paths compatible with all environments"""
    # Get repo root - robust method
    if '__file__' in globals():
        REPO_ROOT = Path(__file__).parent.parent.absolute()
    else:
        # Fallback for when __file__ is not available
        REPO_ROOT = Path.cwd()
    
    # Core paths
    BLUX_MODULES = REPO_ROOT / "blux_modules"
    SECURITY_DIR = BLUX_MODULES / "security"
    SENSORS_DIR = BLUX_MODULES / "sensors"
    
    paths = {
        'REPO_ROOT': REPO_ROOT,
        'BLUX_MODULES': BLUX_MODULES,
        'SECURITY_DIR': SECURITY_DIR,
        'SENSORS_DIR': SENSORS_DIR,
        'TRIP_ENGINE': SECURITY_DIR / "trip_engine.py",
        'DECISIONS_ENGINE': SECURITY_DIR / "decisions_engine.py",
        'SENSORS_MANAGER': SECURITY_DIR / "sensors_manager.py",
        'ANTI_TAMPER_ENGINE': SECURITY_DIR / "anti_tamper_engine.py",
        'RULES_DIR': REPO_ROOT / ".config" / "rules",
        'RULES_PATH': REPO_ROOT / ".config" / "rules" / "rules.json",
        'CONFIG_DIR': REPO_ROOT / ".config" / "blux_guard",
        'LOGS_DIR': REPO_ROOT / "logs",
        'INCIDENTS_LOG': REPO_ROOT / "logs" / "decisions" / "incidents.log",
        'BACKUP_DIR': REPO_ROOT / ".config" / "rules" / "backups",
        'PIDFILE': REPO_ROOT / ".blux-trip.pid",
        'SECURITY_CONFIG': REPO_ROOT / ".config" / "blux_guard" / "security.json"
    }
    
    # Create essential directories
    essential_dirs = [
        paths['RULES_DIR'],
        paths['CONFIG_DIR'], 
        paths['LOGS_DIR'],
        paths['BACKUP_DIR'],
        paths['LOGS_DIR'] / "anti_tamper",
        paths['LOGS_DIR'] / "sensors",
        paths['LOGS_DIR'] / "decisions"
    ]
    
    for directory in essential_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    return paths

PATHS = setup_paths()

# ----------------------
# Security System Setup
# ----------------------
def setup_security() -> SecurityIntegration:
    """Initialize and return security system"""
    if not SECURITY_AVAILABLE:
        logger.warning("Security system not available - running in basic mode")
        return None
    
    try:
        security = SecurityIntegration(PATHS['REPO_ROOT'])
        return security
    except Exception as e:
        logger.error(f"Failed to setup security system: {e}")
        return None

# ----------------------
# Python Detection
# ----------------------
def find_python():
    """Find suitable Python interpreter for current environment"""
    candidates = ["python3", "python"]
    
    # Environment-specific preferences
    if ENVIRONMENT in ["termux", "android"]:
        candidates = ["python", "python3"]  # Termux often uses 'python'
    elif ENVIRONMENT == "macos":
        candidates = ["python3", "python"]  # macOS typically needs python3
    elif ENVIRONMENT == "windows":
        candidates = ["python", "python3", "py"]  # Windows may use 'py'
    
    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "Python 3" in result.stdout:
                # Verify we can import essential modules
                check_result = subprocess.run(
                    [cmd, "-c", "import sys, json, os, time"],
                    capture_output=True,
                    timeout=5
                )
                if check_result.returncode == 0:
                    return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            continue
    
    print(f"❌ No suitable Python 3 interpreter found in environment: {ENVIRONMENT}", file=sys.stderr)
    print("💡 Please install Python 3.7+ and ensure it's in your PATH", file=sys.stderr)
    sys.exit(1)

PYTHON = os.environ.get("PYTHON") or find_python()

# ----------------------
# Core Functions
# ----------------------
def run_trip_engine(foreground=True, security_system=None):
    """Start the trip engine with security checks"""
    # Security check
    if security_system and not security_system.is_authenticated:
        print("❌ Authentication required to start Trip Engine")
        if not security_system.authenticate_user():
            sys.exit(1)
    
    if not PATHS['TRIP_ENGINE'].exists():
        print(f"❌ Trip engine not found at {PATHS['TRIP_ENGINE']}", file=sys.stderr)
        sys.exit(1)
    
    if foreground:
        print(f"🚀 Starting Trip Engine in foreground...")
        print(f"🔧 Using Python: {PYTHON}")
        print(f"📁 Script: {PATHS['TRIP_ENGINE']}")
        
        try:
            subprocess.run(
                [PYTHON, str(PATHS['TRIP_ENGINE'])],
                check=True
            )
        except Exception as e:
            print(f"❌ Failed to start trip engine: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Background process
        if PATHS['PIDFILE'].exists():
            try:
                with open(PATHS['PIDFILE'], 'r') as f:
                    pid = int(f.read().strip())
                # Check if process is still running
                try:
                    os.kill(pid, 0)
                    print(f"⚠️ Trip Engine already running (pid {pid})")
                    return
                except (OSError, ProcessLookupError):
                    # Process not running, remove stale pidfile
                    PATHS['PIDFILE'].unlink(missing_ok=True)
            except (ValueError, IOError):
                PATHS['PIDFILE'].unlink(missing_ok=True)
        
        print(f"🚀 Starting Trip Engine in background...")
        log_file = PATHS['REPO_ROOT'] / "blux-trip.log"
        
        try:
            with open(log_file, 'a') as log_handle:
                process = subprocess.Popen(
                    [PYTHON, str(PATHS['TRIP_ENGINE'])],
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    start_new_session=True  # Detach from parent process group
                )
            
            with open(PATHS['PIDFILE'], 'w') as f:
                f.write(str(process.pid))
            
            print(f"✅ Started with pid {process.pid}, logs -> {log_file}")
            
        except Exception as e:
            print(f"❌ Failed to start background process: {e}", file=sys.stderr)
            sys.exit(1)

def stop_trip_engine(security_system=None):
    """Stop the background trip engine with security checks"""
    # Security check for stop command
    if security_system and not security_system.is_authenticated:
        print("❌ Authentication required to stop Trip Engine")
        if not security_system.authenticate_user():
            sys.exit(1)
    
    if not PATHS['PIDFILE'].exists():
        print(f"ℹ️ No pidfile found at {PATHS['PIDFILE']}")
        return
    
    try:
        with open(PATHS['PIDFILE'], 'r') as f:
            pid = int(f.read().strip())
        
        print(f"🛑 Stopping Trip Engine (pid {pid})...")
        
        # Try graceful termination first
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print(f"⚠️ Process {pid} not found")
            PATHS['PIDFILE'].unlink(missing_ok=True)
            return
        
        # Wait for process to terminate
        for i in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break
        else:
            # Force kill if still running
            try:
                os.kill(pid, signal.SIGKILL)
                print("⚠️ Force killed process")
            except ProcessLookupError:
                pass
        
        PATHS['PIDFILE'].unlink(missing_ok=True)
        print("✅ Trip Engine stopped")
        
    except (ValueError, IOError) as e:
        print(f"❌ Invalid pidfile: {e}")
        PATHS['PIDFILE'].unlink(missing_ok=True)

def feed_event(security_system=None):
    """Feed JSON event from stdin to trip engine"""
    if security_system and not security_system.is_authenticated:
        print("❌ Authentication required to feed events")
        if not security_system.authenticate_user():
            sys.exit(1)
    
    if sys.stdin.isatty():
        print("❌ 'feed' requires JSON input on stdin", file=sys.stderr)
        print("💡 Example:", file=sys.stderr)
        print('  echo \'{"uid":"com.example","network":{"remote_ips_count":60}}\' | blux feed', file=sys.stderr)
        sys.exit(1)
    
    try:
        # Read and validate JSON from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            print("❌ No input received on stdin", file=sys.stderr)
            sys.exit(1)
        
        # Validate JSON
        json.loads(input_data)
        
        # Pass to trip engine
        subprocess.run([PYTHON, str(PATHS['TRIP_ENGINE'])], input=input_data, text=True)
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to process event: {e}", file=sys.stderr)
        sys.exit(1)

def tail_logs(security_system=None):
    """Follow incident logs"""
    if security_system and not security_system.is_authenticated:
        print("❌ Authentication required to view logs")
        if not security_system.authenticate_user():
            sys.exit(1)
    
    incidents_log = PATHS['INCIDENTS_LOG']
    
    # Create file if it doesn't exist
    incidents_log.parent.mkdir(parents=True, exist_ok=True)
    incidents_log.touch(exist_ok=True)
    
    print(f"📋 Tailing incidents log: {incidents_log}")
    print(f"⏹️ Press Ctrl+C to stop")
    
    try:
        # Try to use system tail command first (more efficient)
        subprocess.run(["tail", "-F", str(incidents_log)])
    except (FileNotFoundError, PermissionError):
        # Fallback to Python implementation
        print("ℹ️ Using Python tail fallback...")
        tail_logs_python()

def tail_logs_python():
    """Python-based log tailing fallback"""
    incidents_log = PATHS['INCIDENTS_LOG']
    last_size = incidents_log.stat().st_size if incidents_log.exists() else 0
    
    try:
        while True:
            current_size = incidents_log.stat().st_size if incidents_log.exists() else 0
            
            if current_size > last_size:
                with open(incidents_log, 'r') as f:
                    f.seek(last_size)
                    new_content = f.read()
                    if new_content:
                        print(new_content, end='')
                last_size = current_size
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Stopped tailing logs")
    except Exception as e:
        print(f"❌ Failed to tail logs: {e}", file=sys.stderr)

def install_alias():
    """Install blux alias in shell configuration"""
    shell = os.environ.get('SHELL', '')
    home = Path.home()
    
    # Determine shell rc file
    rc_files = []
    if 'bash' in shell:
        rc_files = [home / '.bashrc', home / '.bash_profile']
    elif 'zsh' in shell:
        rc_files = [home / '.zshrc']
    else:
        # Fallback to common files
        rc_files = [home / '.bashrc', home / '.zshrc', home / '.profile']
    
    rc_file = None
    for candidate in rc_files:
        if candidate.exists():
            rc_file = candidate
            break
    else:
        # No existing rc file, create the first one
        rc_file = rc_files[0]
    
    alias_line = f'alias blux="{PYTHON} {Path(__file__).absolute()}"'
    
    # Check if alias already exists
    if rc_file.exists():
        with open(rc_file, 'r') as f:
            if alias_line in f.read():
                print(f"ℹ️ Alias already exists in {rc_file}")
                return
    
    # Add alias
    with open(rc_file, 'a') as f:
        f.write(f"\n# BLUX Guard CLI alias\n{alias_line}\n")
    
    print(f"✅ Alias added to {rc_file}")
    print(f"🔧 Run 'source {rc_file}' or restart your shell to use the 'blux' command")

def show_status(security_system=None):
    """Show current BLUX Guard status with security information"""
    print(f"🔍 BLUX Guard Status")
    print(f"===================")
    print(f"🌐 Environment: {ENVIRONMENT}")
    print(f"🐍 Python: {PYTHON}")
    print(f"📁 Repo Root: {PATHS['REPO_ROOT']}")
    
    # Security status
    if security_system:
        security_status = security_system.get_security_status()
        print(f"🔐 Security: {'✅ ENABLED' if security_status['security_available'] else '❌ UNAVAILABLE'}")
        print(f"🔓 Authenticated: {'✅ YES' if security_status['authenticated'] else '❌ NO'}")
    
    # Check if trip engine is running
    if PATHS['PIDFILE'].exists():
        try:
            with open(PATHS['PIDFILE'], 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print(f"🚀 Trip Engine: ✅ RUNNING (pid {pid})")
            except (OSError, ProcessLookupError):
                print("🚀 Trip Engine: ❌ NOT RUNNING (stale pidfile)")
                PATHS['PIDFILE'].unlink(missing_ok=True)
        except (ValueError, IOError):
            print("🚀 Trip Engine: ❓ UNKNOWN (corrupted pidfile)")
            PATHS['PIDFILE'].unlink(missing_ok=True)
    else:
        print("🚀 Trip Engine: ❌ NOT RUNNING")
    
    # Check essential files
    print(f"\n📋 Essential Files:")
    print(f"  Trip Engine: {'✅ FOUND' if PATHS['TRIP_ENGINE'].exists() else '❌ MISSING'}")
    print(f"  Rules: {'✅ FOUND' if PATHS['RULES_PATH'].exists() else '❌ MISSING'}")
    print(f"  Incidents Log: {'✅ FOUND' if PATHS['INCIDENTS_LOG'].exists() else '❌ MISSING'}")
    
    # Show privilege information if available
    if security_system and security_system.privilege_mgr:
        security_system.check_privileges_and_warn()

def security_menu(security_system):
    """Security management menu"""
    if not security_system:
        print("❌ Security system not available")
        return
    
    while True:
        print(f"\n🔐 Security Management")
        print(f"=====================")
        print(f"1. Change Password")
        print(f"2. Security Status")
        print(f"3. Emergency Reset")
        print(f"4. Back to Main Menu")
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                if security_system.auth_system and hasattr(security_system.auth_system, 'change_password'):
                    security_system.auth_system.change_password()
                else:
                    print("❌ Password change not available")
                    
            elif choice == "2":
                status = security_system.get_security_status()
                print(f"\n🔐 Security Status:")
                print(f"   Authenticated: {'✅ YES' if status['authenticated'] else '❌ NO'}")
                if 'authentication' in status:
                    auth = status['authentication']
                    if 'password_set' in auth:
                        print(f"   Password Set: {'✅ YES' if auth['password_set'] else '❌ NO'}")
                    if 'failed_attempts' in auth:
                        print(f"   Failed Attempts: {auth['failed_attempts']}/{auth.get('max_attempts', 5)}")
                
            elif choice == "3":
                security_system.emergency_reset()
                
            elif choice == "4":
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n⏹️ Operation cancelled")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def usage():
    """Show usage information"""
    print(f"""
🔒 BLUX Guard CLI - Multi-Environment Security Monitor
🌐 Environment: {ENVIRONMENT}
🐍 Python: {PYTHON}

Usage: {sys.argv[0]} <command> [args]

Commands:
  start        Run Trip Engine in foreground
  start-bg     Run Trip Engine in background
  stop         Stop background Trip Engine
  status       Show current status
  feed         Feed JSON event from stdin to engine
  tail         Follow incident logs
  security     Security management menu
  install-alias Add 'blux' alias to shell configuration
  help         Show this help

Examples:
  {sys.argv[0]} start           # Run in foreground
  {sys.argv[0]} start-bg        # Run in background  
  {sys.argv[0]} stop            # Stop background process
  echo '{{"event":"test"}}' | {sys.argv[0]} feed
  {sys.argv[0]} tail            # Follow incident logs
  {sys.argv[0]} security        # Security management
  {sys.argv[0]} install-alias   # Install shell alias

Paths:
  📁 Repo Root: {PATHS['REPO_ROOT']}
  📋 Rules: {PATHS['RULES_PATH']}
  📊 Logs: {PATHS['LOGS_DIR']}
  🔧 PID File: {PATHS['PIDFILE']}
""")

# ----------------------
# Command Dispatcher
# ----------------------
def main():
    # Initialize security system
    security_system = setup_security()
    
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "start":
            run_trip_engine(foreground=True, security_system=security_system)
        elif command == "start-bg":
            run_trip_engine(foreground=False, security_system=security_system)
        elif command == "stop":
            stop_trip_engine(security_system=security_system)
        elif command == "status":
            show_status(security_system=security_system)
        elif command == "feed":
            feed_event(security_system=security_system)
        elif command == "tail":
            tail_logs(security_system=security_system)
        elif command == "security":
            security_menu(security_system)
        elif command == "install-alias":
            install_alias()
        elif command in ("help", "-h", "--help"):
            usage()
        else:
            print(f"❌ Unknown command: {command}", file=sys.stderr)
            usage()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Command failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
