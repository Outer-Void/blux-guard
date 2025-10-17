#!/usr/bin/env python3
"""
BLUX Guard Security System Setup
Cross-platform installation, secure first-run password setup,
and integration for BLUX Guard.
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import stat
import getpass
import logging

# Optional: Argon2 for password hashing
try:
    from argon2 import PasswordHasher
    ARGON2_AVAILABLE = True
except ImportError:
    PasswordHasher = None
    ARGON2_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("blux_setup")

# Directories used by BLUX Guard - use absolute paths
BASE_DIR = Path.cwd()
CONFIG_DIR = Path.home() / ".config" / "blux_guard"
LOG_DIRS = [
    BASE_DIR / "logs/anti_tamper",
    BASE_DIR / "logs/sensors",
    BASE_DIR / "logs/decisions"
]
SCRIPTS_DIR = BASE_DIR / "scripts"
DOCS_DIR = BASE_DIR / "docs/assets"
LOCK_FILE = CONFIG_DIR / "lock.hash"

# ----------------- Utility Functions ----------------- #

def is_root() -> bool:
    """Detect root privileges across platforms."""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0

def check_python_version():
    """Ensure Python >= 3.7"""
    if sys.version_info < (3, 7):
        logger.error("Python 3.7 or higher required")
        sys.exit(1)
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor} - OK")

def create_virtual_environment() -> Path:
    """Create a virtual environment and return its path."""
    venv_path = BASE_DIR / ".venv"
    try:
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        logger.info(f"Virtual environment created at: {venv_path}")
        return venv_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        sys.exit(1)

def activate_virtual_environment(venv_path: Path):
    """Activate the virtual environment (prints instructions)."""
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        activate_script = venv_path / "bin" / "activate"

    print(f"\nActivate the virtual environment by running:\n{activate_script}\n")
    print(f"Then rerun this setup script to install dependencies correctly.\n")
    sys.exit(0)  # Exit to force the user to activate

def install_dependencies(venv_path: Path):
    """Install required Python packages within the virtual environment."""
    pip_executable = venv_path / "bin" / "pip" if platform.system() != "Windows" else venv_path / "Scripts" / "pip.exe"
    dependencies = []
    requirements_file = BASE_DIR / "requirements.txt"
    
    if requirements_file.exists():
        logger.info("Installing dependencies from requirements.txt")
        try:
            subprocess.check_call([str(pip_executable), "install", "-r", str(requirements_file)])
            return  # Exit the function early after successful installation from requirements.txt
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies from requirements.txt: {e}")
            print("Failed to install dependencies from requirements.txt. Please check the logs.")
            sys.exit(1)
    else:
        dependencies = [
            "argon2-cffi",
            "cryptography",
            "textual",
            "rich",
            "psutil"
        ]

        for pkg in dependencies:
            try:
                subprocess.check_call([str(pip_executable), "install", pkg])
                logger.info(f"Dependency installed: {pkg}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependency: {pkg} - Error: {e}")
                print("Failed to install all required dependencies. Please check the logs.")
                sys.exit(1)

def setup_directories():
    """Create necessary directories for logs, scripts, and docs."""
    all_dirs = LOG_DIRS + [SCRIPTS_DIR, DOCS_DIR, CONFIG_DIR]

    for directory in all_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created or exists: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            # Exit if directory creation fails, as it may cause issues later
            print("Failed to create necessary directories. Please check the logs.")
            sys.exit(1)

def set_secure_permissions():
    """Set safe file permissions for Unix-like systems."""
    if platform.system() in ["Linux", "Darwin"]:
        # Check if we have permission to change permissions
        if not os.access(str(SCRIPTS_DIR), os.W_OK) or not os.access(str(CONFIG_DIR), os.W_OK):
            logger.warning("Insufficient permissions to set secure file permissions.")
            print("Insufficient permissions to set secure file permissions. Run as root/sudo.")
            return

        # Make scripts executable if they exist
        if SCRIPTS_DIR.exists():
            for script in SCRIPTS_DIR.glob("*.sh"):
                try:
                    script.chmod(0o755)
                    logger.info(f"Set executable: {script}")
                except Exception as e:
                    logger.warning(f"Could not set permissions for {script}: {e}")

        # Secure config files
        if CONFIG_DIR.exists():
            for item in CONFIG_DIR.rglob("*"):
                if item.is_file():
                    try:
                        item.chmod(0o600)
                        logger.info(f"Secured: {item}")
                    except Exception as e:
                        logger.warning(f"Could not secure {item}: {e}")

def setup_lock():
    """First-run password setup for BLUX Guard."""
    if LOCK_FILE.exists():
        logger.info("Existing lock file detected. Skipping password setup.")
        return

    if not ARGON2_AVAILABLE:
        logger.error("argon2-cffi not installed; cannot create secure lock.")
        print("argon2-cffi is required for secure password storage. Please install it and rerun setup.")
        sys.exit(1)

    ph = PasswordHasher()
    print("\n--- BLUX Guard First-Run Setup ---")
    print("Set a secure password for BLUX Guard access")

    max_attempts = 3
    for attempt in range(max_attempts):
        password = getpass.getpass("Create a password or PIN: ").strip()

        if not password:
            print("Password cannot be empty. Please try again.")
            continue

        if len(password) < 4:
            print("Password must be at least 4 characters. Please try again.")
            continue

        confirm = getpass.getpass("Confirm password: ").strip()

        if password == confirm:
            try:
                hashed = ph.hash(password)
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)

                # Atomic lock file creation
                tmp_lock_file = CONFIG_DIR / "lock.tmp"
                tmp_lock_file.write_text(hashed)
                if platform.system() != "Windows":
                    tmp_lock_file.chmod(0o600)  # Set permissions BEFORE rename
                tmp_lock_file.rename(LOCK_FILE) # Atomic rename

                logger.info(f"Password stored securely at {LOCK_FILE}")
                print("Password setup completed successfully!")
                return
            except Exception as e:
                logger.error(f"Failed to create lock file: {e}")
                print("Failed to create lock file. Please check the logs.")
                sys.exit(1)  # Exit on failure
        else:
            remaining = max_attempts - attempt - 1
            if remaining > 0:
                print(f"Passwords do not match. {remaining} attempts remaining.")
            else:
                logger.error("Too many failed attempts. Password setup failed.")
                print("Password setup failed. You can run setup again to set a password.")
                sys.exit(1) # Exit on failure

def check_root_warnings():
    """Warn user about full features in root mode vs safe alternatives."""
    if is_root():
        logger.info("Running as ROOT: full system features enabled")
        print("⚠️  Running as administrator/root - system-level monitoring enabled")
    else:
        logger.warning("Non-root detected: some system-level features will use safe fallbacks.")
        print("ℹ️  Running as standard user - some features limited")

# ----------------- Main Setup Routine ----------------- #

def main():
    print("BLUX Guard Security System Setup")
    print("=" * 50)

    try:
        check_python_version()

        # Virtual environment setup
        venv_path = create_virtual_environment()
        activate_virtual_environment(venv_path)  # This will exit the script

        # Install dependencies within the virtual environment
        install_dependencies(venv_path)

        # Recheck for Argon2 availability after installation
        try:
            from argon2 import PasswordHasher  # Re-import to check
            global ARGON2_AVAILABLE
            ARGON2_AVAILABLE = True
        except ImportError:
            ARGON2_AVAILABLE = False

        setup_directories()
        set_secure_permissions()
        setup_lock()
        check_root_warnings()

        print("\n✅ Setup complete!")
        print("Run: python initiate_cockpit.py to start BLUX Guard\n")
        logger.info("BLUX Guard setup finished successfully.")

    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
