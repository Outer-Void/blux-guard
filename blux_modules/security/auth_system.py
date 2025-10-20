import os
from pathlib import Path
import sys
import time
import hmac
import hashlib
import json
import logging
import platform
import secrets
import base64
import sqlite3
from typing import Dict, Any

# Conditional imports for optional dependencies
HAS_CRYPTOGRAPHY = False
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.exceptions import InvalidKey
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    print("Cryptography library not found. Install with: pip install cryptography")

HAS_ARGON2 = False
try:
    import argon2
    HAS_ARGON2 = True
except ImportError:
    print("Argon2 library not found. Install with: pip install argon2-cffi")

# --- Configuration ---
class AuthSystem:
    """Secure authentication system for BLUX Guard with cross-platform support"""

    def __init__(self, app_name: str = "blux_guard"):
        """Initialize authentication system"""

        self.app_name = app_name
        self.platform = platform.system()

        # Configuration directories
        self.config_dir = Path.home() / ".config" / self.app_name
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "auth_config.json"
        self.lock_file = self.config_dir / "lock.hash"
        self.db_file = self.config_dir / "attempts.db"

        # Logger setup
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        log_file = self.config_dir / "auth_system.log"
        file_handler = logging.FileHandler(str(log_file))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Defaults
        self.min_password_length = 8
        self.max_attempts = 5
        self.lockout_duration = 900  # seconds (15 minutes)
        self.enable_biometric_fallback = False

        # Argon2 Configuration
        self.argon2_time_cost = 3
        self.argon2_memory_cost = 65536
        self.argon2_parallelism = 1

        # Load configuration
        self.config = self._load_config()

        # Override Argon2 settings from config, if available
        self.argon2_time_cost = self.config.get("argon2_time_cost", self.argon2_time_cost)
        self.argon2_memory_cost = self.config.get("argon2_memory_cost", self.argon2_memory_cost)
        self.argon2_parallelism = self.config.get("argon2_parallelism", self.argon2_parallelism)

        # Database initialization
        self._create_table()

    def _load_config(self) -> Dict[str, Any]:
        """Load authentication configuration with defaults"""
        default_config = {
            "auth_method": "pbkdf2" if HAS_CRYPTOGRAPHY else "basic",
            "min_password_length": self.min_password_length,
            "max_attempts": self.max_attempts,
            "lockout_duration": self.lockout_duration,
            "enable_biometric": self.enable_biometric_fallback,
            "created": time.time(),
            "version": "1.0.0",
            "security_level": "high",
            "argon2_time_cost": self.argon2_time_cost, # Added Argon2 settings
            "argon2_memory_cost": self.argon2_memory_cost,
            "argon2_parallelism": self.argon2_parallelism
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Validate keys
                # Avoid logging sensitive key names
                sensitive_keys = {"min_password_length", "password", "secret", "token", "passcode", "api_key"}
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                        if key not in sensitive_keys:
                            self.logger.warning("Missing non-sensitive configuration key in config. Using default value.")

            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"Error loading config, using defaults: {e}")
                self.logger.warning(f"Could not load config, using defaults: {e}")
                config = default_config
        else:
            config = default_config

        # Save the validated config back to file
        self._save_config(config)
        return config

    def _save_config(self, config: Dict[str, Any] = None):
        """Save current configuration to file"""
        if config is None:
            config = self.config  # Use the current config if none is provided
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            if sys.platform != "win32":
                os.chmod(self.config_file, 0o600)
            self.config = config  # Update current config
            self.logger.debug("Config saved successfully")
        except Exception as e:
            print(f"Could not save config file: {e}")
            self.logger.error(f"Could not save config file: {e}")

    def hash_password(self, password: str) -> str:
        """Hash the password using the configured method"""
        auth_method = self.config.get("auth_method", "pbkdf2")  # Default to PBKDF2

        try:
            if auth_method == "argon2" and HAS_ARGON2:
                return f"argon2${self._hash_password_argon2(password)}"
            elif auth_method == "pbkdf2" or not HAS_ARGON2:
                return f"pbkdf2_sha256${self._hash_password_pbkdf2(password)}"
            else:
                return f"basic${self._hash_password_basic(password)}"  # Least secure, fallback only
        except ImportError as e:
            print(f"Hashing error: {e}")
            self.logger.error(f"Hashing error: {e}")
            return f"basic${self._hash_password_basic(password)}" # Final fallback

    def _hash_password_pbkdf2(self, password: str) -> str:
        """Hash password using PBKDF2-HMAC-SHA256"""
        if HAS_CRYPTOGRAPHY:
            salt = os.urandom(16)
            iterations = 100000

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            salt_hex = salt.hex()
            key_hex = key.hex()
            return f"{iterations}${salt_hex}${key_hex}"
        else:  # Fallback
            salt = secrets.token_hex(16)
            iterations = 100000
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
            salt_hex = salt
            key_hex = key.hex()
            return f"{iterations}${salt_hex}${key_hex}"

    def _hash_password_argon2(self, password: str) -> str:
        """Hash password using Argon2 (most secure)"""
        if not HAS_ARGON2:
            raise ImportError("Argon2 not available")

        ph = argon2.PasswordHasher(
            time_cost=self.argon2_time_cost,
            memory_cost=self.argon2_memory_cost,
            parallelism=self.argon2_parallelism,
            hash_len=32,
            salt_len=16
        )
        return ph.hash(password)

    def _hash_password_basic(self, password: str) -> str:
        """Fallback: Use PBKDF2-HMAC-SHA256 for password hashing with random salt and sufficient iterations"""
        salt = secrets.token_hex(16)
        iterations = 100000
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        salt_hex = salt
        key_hex = key.hex()
        return f"{iterations}${salt_hex}${key_hex}"

    def verify_password(self, password: str, hash_string: str) -> bool:
        """Verify password against stored hash"""
        try:
            if hash_string.startswith("argon2"):
                if not HAS_ARGON2:
                    return False
                ph = argon2.PasswordHasher()
                try:
                    return ph.verify(hash_string, password)
                except argon2.exceptions.VerifyMismatchError:
                    return False
                except argon2.exceptions.InvalidHashError:
                    return False
                except Exception as e:  # Catch unexpected Argon2 errors
                    self.logger.error(f"Argon2 verification error: {e}")
                    return False

            elif hash_string.startswith("pbkdf2_sha256"):
                try:
                    _, iterations, salt_hex, key_hex = hash_string.split('$')
                    salt = bytes.fromhex(salt_hex)
                    stored_key = bytes.fromhex(key_hex)

                    if HAS_CRYPTOGRAPHY:
                        kdf = PBKDF2HMAC(
                            algorithm=hashes.SHA256(),
                            length=32,
                            salt=salt,
                            iterations=int(iterations),
                            backend=default_backend()
                        )
                        computed_key = kdf.derive(password.encode('utf-8'))
                    else:
                        computed_key = hashlib.pbkdf2_hmac(
                            'sha256', password.encode('utf-8'), salt, int(iterations)
                        )

                    return hmac.compare_digest(computed_key, stored_key)
                except (ValueError, KeyError, binascii.Error) as e: # Catch specific exceptions
                    self.logger.error(f"PBKDF2 parsing/verification error: {e}")
                    return False
                except Exception as e: # Catch unexpected PBKDF2 errors
                    self.logger.error(f"PBKDF2 verification error: {e}")
                    return False

            elif hash_string.startswith("basic"):
                try:
                    # New format: basic$iterations$salt_hex$key_hex
                    _, iterations, salt_hex, key_hex = hash_string.split('$')
                    salt = bytes.fromhex(salt_hex)
                    stored_key = bytes.fromhex(key_hex)
                    computed_key = hashlib.pbkdf2_hmac(
                        'sha256', password.encode('utf-8'), salt, int(iterations)
                    )
                    return hmac.compare_digest(computed_key, stored_key)
                except (ValueError, KeyError) as e:
                    self.logger.error(f"Basic hash parsing error: {e}")
                    return False
                except Exception as e: # Catch unexpected basic hash errors
                    self.logger.error(f"Basic hash verification error: {e}")
                    return False

            else:
                # Legacy format or unknown
                return False

        except Exception as e:
            self.logger.error(f"Password verification error: {e}") # General error catch
            return False

    def setup_password(self, password: str) -> bool:
        """Set up initial password with safety checks"""
        if self.lock_file.exists():
            print("Password already set up. Use change_password() to modify.")
            return False

        if not password:  # Check if password is provided
            print("No password provided.")
            return False

        try:
            password_hash = self.hash_password(password)
            with open(self.lock_file, 'w', encoding='utf-8') as f:
                f.write(password_hash)

            if sys.platform != "win32":
                os.chmod(self.lock_file, 0o600)

            # self.record_successful_attempt() # Don't record attempt here!
            self._save_config()
            print("Password set up successfully!")
            self.logger.info("Password setup completed successfully")
            return True

        except Exception as e:
            print(f"Error setting up password: {e}")
            self.logger.error(f"Password setup failed: {e}")
            return False

    def change_password(self, password: str) -> bool:
        """Change existing password with verification"""

        if not password:  # Check if password is provided
            print("No password provided.")
            return False

        try:
            password_hash = self.hash_password(password)
            with open(self.lock_file, 'w', encoding='utf-8') as f:
                f.write(password_hash)

            print("Password changed successfully!")
            self.logger.info("Password changed successfully")
            return True

        except Exception as e:
            print(f"Error changing password: {e}")
            self.logger.error(f"Password change failed: {e}")
            return False

    def _get_attempt_data(self) -> Dict[str, Any]:
        """Get login attempt data securely"""
        default_data = {"attempts": 0, "last_attempt": 0.0, "locked_until": 0.0}

        try:
            conn = self._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT attempts, last_attempt, locked_until FROM attempts WHERE id = 1")
                row = cursor.fetchone()
                conn.close()
                if row:
                    return {"attempts": row[0], "last_attempt": row[1], "locked_until": row[2]}
                else:
                    self._create_initial_record()  # Create initial record if not found
                    return default_data
        except Exception as e:
            self.logger.warning(f"Could not load attempt data: {e}")
            return default_data.copy()

    def _create_initial_record(self):
        """Create initial record"""
        try:
            conn = self._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO attempts (id, attempts, last_attempt, locked_until) VALUES (1, 0, 0.0, 0.0)")
                conn.commit()
                conn.close()
        except Exception as e:
            self.logger.error(f"Error creating initial record: {e}")

    def _save_attempt_data(self, data: Dict[str, Any]):
        """Save login attempt data securely"""
        try:
            conn = self._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE attempts
                    SET attempts = ?, last_attempt = ?, locked_until = ?
                    WHERE id = 1
                """, (data["attempts"], data["last_attempt"], data["locked_until"]))
                conn.commit()
                conn.close()
        except Exception as e:
            self.logger.error(f"Could not save attempt data: {e}")

    def _get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            return None

    def _create_table(self):
        """Create table if not exists"""
        try:
            conn = self._get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS attempts (
                        id INTEGER PRIMARY KEY,
                        attempts INTEGER DEFAULT 0,
                        last_attempt REAL DEFAULT 0.0,
                        locked_until REAL DEFAULT 0.0
                    )
                """)
                conn.commit()
                conn.close()
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")

    def is_locked_out(self) -> bool:
        """Check if account is temporarily locked due to failed attempts"""
        attempt_data = self._get_attempt_data()
        current_time = time.time()

        # Check if locked out
        if attempt_data.get("locked_until", 0.0) > current_time:
            return True

        # Reset attempts if lockout period has passed
        if attempt_data.get("attempts", 0) >= self.max_attempts:
            if attempt_data.get("last_attempt", 0.0) + self.lockout_duration < current_time:
                attempt_data["attempts"] = 0
                attempt_data["locked_until"] = 0.0
                self._save_attempt_data(attempt_data)
                return False
            return True

        return False

    def record_failed_attempt(self):
        """Record a failed login attempt"""
        attempt_data = self._get_attempt_data()
        current_time = time.time()

        attempt_data["attempts"] = attempt_data.get("attempts", 0) + 1
        attempt_data["last_attempt"] = current_time

        # Lock account if max attempts reached
        if attempt_data["attempts"] >= self.max_attempts:
            lock_duration = self.lockout_duration
            attempt_data["locked_until"] = current_time + lock_duration
            self.logger.warning(f"Account locked for {lock_duration // 60} minutes due to failed attempts")

        self._save_attempt_data(attempt_data)

    def record_successful_attempt(self):
        """Reset failed attempts on successful login"""
        attempt_data = self._get_attempt_data()
        attempt_data["attempts"] = 0
        attempt_data["locked_until"] = 0.0
        self._save_attempt_data(attempt_data)
        self.logger.debug("Successful login recorded")

    def get_security_status(self) -> Dict[str, Any]:
        """Get security status"""
        # Check if lock file exists
        password_set = self.lock_file.exists()

        # Get lockout status
        locked_out = self.is_locked_out()

        # Get attempt data
        attempt_data = self._get_attempt_data()
        failed_attempts = attempt_data.get("attempts", 0)
        auth_method = self.config.get("auth_method", "pbkdf2")

        return {
            "password_set": password_set,
            "failed_attempts": failed_attempts,
            "max_attempts": self.max_attempts,
            "locked_out": locked_out,
            "auth_method": auth_method,
        }
