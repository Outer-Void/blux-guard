"""
BLUX Guard CLI Security Integration
Unified security system with authentication and privilege management
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import logging
import getpass
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class SecurityIntegration:
    """
    Unified security system for BLUX Guard CLI
    Integrates authentication, privilege management, and security features
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.auth_system = None
        self.privilege_mgr = None
        self.is_authenticated = False
        
        # Initialize security systems
        self._init_security_systems()
    
    def _init_security_systems(self):
        """Initialize security systems with error handling"""
        try:
            # Import security modules
            from blux_modules.security.auth_system import AuthSystem
    # PrivilegeManager imported conditionally below
            
            self.auth_system = AuthSystem()
            self.privilege_mgr = PrivilegeManager()
            logger.info("Security systems initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Security modules not available: {e}")
            self._create_fallback_security()
        except Exception as e:
            logger.error(f"Failed to initialize security systems: {e}")
            self._create_fallback_security()
    
    def _create_fallback_security(self):
        """Create fallback security systems when main modules are unavailable"""
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

            def emergency_reset(self) -> bool:
                """Emergency security reset"""
                config_dir = Path.home() / ".config" / "blux_guard"
                if config_dir.exists():
                    import shutil
                    shutil.rmtree(config_dir)
                    print("✅ Security configuration removed")
                print("🔧 Restart the application to set up new security credentials")
                return True

        class FallbackPrivilege:
            def get_privilege_info(self):
                is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
                return {"is_root": is_root, "fallback": True}

        self.auth_system = FallbackAuth()
        self.privilege_mgr = FallbackPrivilege()
    
    def authenticate_user(self, max_attempts: int = 3) -> bool:
        """
        Authenticate user with security system
        Returns True if authenticated, False otherwise
        """
        if self.auth_system is None:
            logger.error("Authentication system not available")
            return False
        
        try:
            # Check if first run
            if self.auth_system.is_first_run():
                print("\n🔐 BLUX Guard First Run Setup")
                print("=" * 40)
                print("Setting up security system...")
                
                if not self.auth_system.setup_password():
                    print("❌ Security setup failed")
                    return False
                
                print("✅ Security system configured successfully")
            
            # Authenticate user
            print("\n🔐 BLUX Guard Authentication")
            print("=" * 40)
            
            for attempt in range(max_attempts):
                if self.auth_system.authenticate():
                    self.is_authenticated = True
                    print("✅ Authentication successful")
                    return True
                
                remaining = max_attempts - attempt - 1
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
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        status = {
            "authenticated": self.is_authenticated,
            "security_available": self.auth_system is not None and self.privilege_mgr is not None
        }
        
        if self.auth_system:
            try:
                auth_status = self.auth_system.get_security_status()
                status.update({"authentication": auth_status})
            except Exception as e:
                logger.warning(f"Could not get auth status: {e}")
                status["authentication"] = {"error": str(e)}
        
        if self.privilege_mgr:
            try:
                privilege_info = self.privilege_mgr.get_privilege_info()
                status.update({"privileges": privilege_info})
            except Exception as e:
                logger.warning(f"Could not get privilege info: {e}")
                status["privileges"] = {"error": str(e)}
        
        return status
    
    def check_privileges_and_warn(self):
        """Check privileges and display warnings/alternatives"""
        if not self.privilege_mgr:
            print("⚠️  Privilege management not available")
            return
        
        try:
            priv_info = self.privilege_mgr.get_privilege_info()
            
            print(f"\n🖥️  System Information")
            print(f"   Platform: {priv_info.get('platform', {}).get('system', 'Unknown')}")
            print(f"   Architecture: {priv_info['platform']['architecture']}")
            print(f"   Root Access: {'✅ YES' if priv_info['is_root'] else '❌ NO'}")
            
            if not priv_info['is_root']:
                print(f"\n🔒 Running in User Space Mode")
                print("   Some features may be limited. Safe alternatives:")
                
                for feature, alternative in priv_info['safe_alternatives'].items():
                    print(f"   • {feature}: {alternative}")
            
            # Show recommendations
            if priv_info['recommended_actions']:
                print(f"\n💡 Recommendations:")
                for action in priv_info['recommended_actions']:
                    print(f"   • {action}")
                    
        except Exception as e:
            logger.error(f"Privilege check failed: {e}")
            print(f"⚠️  Could not check system privileges: {e}")
    
    def emergency_reset(self) -> bool:
        """Emergency reset of security system"""
        if not self.auth_system:
            print("❌ Authentication system not available")
            return False
        
        try:
            print("\n🚨 EMERGENCY SECURITY RESET")
            print("=" * 50)
            print("⚠️  WARNING: This will remove ALL authentication data!")
            print("⚠️  Only use this if you are locked out of the system!")
            print("=" * 50)
            
            confirm = input("Type 'RESET SECURITY' to confirm: ")
            if confirm != "RESET SECURITY":
                print("❌ Reset cancelled")
                return False
            
            # Use the auth system's emergency reset if available
            if hasattr(self.auth_system, 'emergency_reset'):
                return self.auth_system.emergency_reset()
            else:
                print("❌ Emergency reset not supported in current security system")
                return False
                
        except KeyboardInterrupt:
            print("\n⏹️  Reset cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Emergency reset failed: {e}")
            print(f"❌ Reset failed: {e}")
            return False
