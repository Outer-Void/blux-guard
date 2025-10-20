"""
Root privilege detection and management with safe fallbacks
Enhanced for cross-platform compatibility
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import platform
import subprocess
import logging
import socket
import time
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logger = logging.getLogger(__name__)

class PrivilegeManager:
    """Manage root privileges and provide safe fallbacks across all platforms"""

    def __init__(self):
        self.is_root = self._check_root_privileges()
        self.platform_info = self._get_platform_info()
        self.capabilities = self._detect_capabilities()
        self.safe_alternatives = self._get_safe_alternatives()

        logger.info(f"Privilege manager initialized: root={self.is_root}, platform={self.platform_info['system']}")

    def _check_root_privileges(self) -> bool:
        """Check if running with root privileges across all platforms"""
        try:
            # Primary check for Unix-like systems
            if hasattr(os, 'geteuid'):
                return os.geteuid() == 0

            # Windows admin check
            if sys.platform == 'win32':
                try:
                    import ctypes
                    return ctypes.windll.shell32.IsUserAnAdmin() != 0
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Windows admin check using ctypes failed: {e}")
                    # Fallback for Windows without ctypes
                    try:
                        result = subprocess.run(
                            ['net', 'session'],
                            capture_output=True,
                            timeout=10,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                        return result.returncode == 0
                    except (OSError, subprocess.TimeoutExpired) as e:
                        logger.debug(f"Windows admin check using 'net session' failed: {e}")

            # Android root check
            if self._is_android():
                try:
                    # Check for su binary
                    result = subprocess.run(
                        ['which', 'su'],
                        capture_output=True,
                        timeout=5,
                        text=True # For consistent result type
                    )
                    if result.returncode == 0:
                        # Test if we can use su
                        test_cmd = ['su', '-c', 'id']  # safer way to test su access
                        result = subprocess.run(
                            test_cmd,
                            capture_output=True,
                            timeout=5,
                            text=True # For consistent result type
                        )
                        return 'uid=0(' in result.stdout
                except (OSError, subprocess.TimeoutExpired) as e:
                    logger.debug(f"Android root check failed: {e}")

            return False

        except Exception as e:
            logger.warning(f"Root privilege check failed: {e}")
            return False

    def _is_android(self) -> bool:
        """Check if running on Android"""
        return ('ANDROID_ROOT' in os.environ or
                'TERMUX_VERSION' in os.environ or
                hasattr(os, 'system') and os.system('getprop ro.build.version.sdk > /dev/null 2>&1') == 0)

    def _is_termux(self) -> bool:
        """Check if running in Termux environment"""
        return 'TERMUX_VERSION' in os.environ

    def _get_platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information"""
        system = platform.system().lower()
        is_android = self._is_android()
        is_termux = self._is_termux()

        info = {
            'system': system,
            'is_android': is_android,
            'is_termux': is_termux,
            'is_windows': system == 'windows',
            'is_linux': system == 'linux' and not is_android,
            'is_macos': system == 'darwin',
            'architecture': platform.machine(),
            'release': platform.release(),
            'version': platform.version()
        }

        # Enhanced Android detection
        if is_android:
            try:
                # Get Android version
                result = subprocess.run(
                    ['getprop', 'ro.build.version.release'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    info['android_version'] = result.stdout.strip()
            except (OSError, subprocess.TimeoutExpired) as e:
                logger.debug(f"Could not get Android version: {e}")

        return info

    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect available system capabilities with safe fallbacks"""
        caps = {
            'root_access': self.is_root,
            'system_commands': False,
            'network_admin': False,
            'process_management': False,
            'filesystem_admin': False,
            'hardware_access': False,
            'package_management': False
        }

        # Test basic system command execution
        try:
            if self.platform_info['is_windows']:
                if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                    subprocess.run(
                        ['cmd', '/c', 'echo', 'test'],
                        capture_output=True, timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    subprocess.run(
                        ['cmd', '/c', 'echo', 'test'],
                        capture_output=True, timeout=5
                    )
            else:
                subprocess.run(
                    ['echo', 'test'],
                    capture_output=True, timeout=5
                )
            caps['system_commands'] = True
        except (OSError, subprocess.TimeoutExpired) as e:
            logger.debug(f"System commands test failed: {e}")

        # Test file system access
        test_file = None
        try:
            if self.platform_info['is_windows']:
                test_file = os.path.join(os.environ.get('TEMP', 'C:\\temp'), 'blux_test.txt')
            else:
                test_file = '/tmp/blux_test.txt'

            with open(test_file, 'w') as f:
                f.write('test')
            caps['filesystem_admin'] = True
        except (OSError, PermissionError) as e:
            logger.debug(f"Filesystem access test failed: {e}")
        finally:
            if test_file:
                try:
                    os.unlink(test_file)
                except OSError as e:
                    logger.debug(f"Could not clean up test file: {e}") # Log if delete fails

        # Network capabilities (safe test)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.bind(('127.0.0.1', 0)) # Changed from specific port
            s.close()
            caps['network_admin'] = True
        except (OSError, PermissionError, ImportError) as e:
            logger.debug(f"Network capabilities test failed: {e}")

        # Process management
        try:
            import psutil
            # Safe process listing test
            list(psutil.process_iter(attrs=['pid', 'name'])[:5])
            caps['process_management'] = True
        except (ImportError, OSError, PermissionError) as e:
            logger.debug(f"Process management test failed: {e}")

        return caps

    def _get_safe_alternatives(self) -> Dict[str, str]:
        """Get safe alternatives for restricted operations"""
        alternatives = {
            'network_monitoring': 'User-space socket monitoring via psutil',
            'process_management': 'Process listing via psutil (limited)',
            'file_monitoring': 'Inotify/watchdog for user-owned files',
            'system_hardening': 'App-specific security policies',
            'package_management': 'User-space package verification'
        }

        if self.platform_info['is_android']:
            alternatives.update({
                'network_monitoring': 'Termux netstat / ifconfig commands',
                'process_management': 'ps command via Termux',
                'file_monitoring': 'User directory monitoring only',
                'system_hardening': 'App-level security controls'
            })

        if self.platform_info['is_windows']:
            alternatives.update({
                'network_monitoring': 'Windows netstat command',
                'process_management': 'Windows Tasklist command',
                'file_monitoring': 'Windows filesystem watcher',
                'system_hardening': 'Windows security policies'
            })

        return alternatives

    def get_privilege_info(self) -> Dict[str, Any]:
        """Get comprehensive privilege information"""
        return {
            'is_root': self.is_root,
            'platform': self.platform_info,
            'capabilities': self.capabilities,
            'safe_alternatives': self.safe_alternatives,
            'recommended_actions': self._get_recommended_actions(),
            'limitations': self._get_limitations()
        }

    def _get_recommended_actions(self) -> List[str]:
        """Get recommended actions based on privilege level"""
        actions = []

        if not self.is_root:
            if self.platform_info['is_linux']:
                actions.append("Run with 'sudo' for full system monitoring capabilities")
            elif self.platform_info['is_windows']:
                actions.append("Run as Administrator for full system access")
            elif self.platform_info['is_android'] and self.platform_info['is_termux']:
                actions.append("Grant Termux required permissions for enhanced features")

            actions.append("Some security features will run in user-space mode")
            actions.append("File monitoring limited to user-owned directories")

        if self.is_root:
            actions.append("🔴 FULL SYSTEM ACCESS ENABLED - Use with extreme caution")
            actions.append("Consider running in unprivileged mode for daily use")
            actions.append("Monitor system resources carefully")

        # Platform-specific recommendations
        if self.platform_info['is_android']:
            actions.append("Android environment detected - some system features may be restricted")

        return actions

    def _get_limitations(self) -> List[str]:
        """Get current limitations based on privilege level"""
        limitations = []

        if not self.is_root:
            limitations.append("Cannot monitor system-wide processes")
            limitations.append("Limited network interface control")
            limitations.append("Cannot access other users' files")
            limitations.append("System service management restricted")

        if self.platform_info['is_android']:
            limitations.append("Android security sandbox restrictions apply")
            if not self.platform_info['is_termux']:
                limitations.append("Standard Android environment - limited system access")

        return limitations

    def can_elevate_privileges(self) -> Tuple[bool, str]:
        """Check if privilege elevation is possible and return method"""
        if self.is_root:
            return True, "Already running as root/administrator"

        method = ""
        possible = False

        if self.platform_info['is_windows']:
            try:
                import ctypes
                possible = ctypes.windll.shell32.IsUserAnAdmin() != 0
                method = "Run as Administrator"
            except (ImportError, AttributeError):
                possible = False
                method = "Administrator access not available"
        else:
            # Unix-like systems
            try:
                result = subprocess.run(
                    ['which', 'sudo'],
                    capture_output=True, timeout=5
                )
                if result.returncode == 0:
                    possible = True
                    method = "Use 'sudo' command"
                else:
                    # Check for doas (OpenBSD)
                    result = subprocess.run(
                        ['which', 'doas'],
                        capture_output=True, timeout=5
                    )
                    if result.returncode == 0:
                        possible = True
                        method = "Use 'doas' command"
                    else:
                        method = "No privilege elevation method found"
            except (OSError, subprocess.TimeoutExpired):
                method = "Cannot determine elevation method"

        return possible, method

    def get_operational_mode(self) -> str:
        """Get current operational mode description"""
        if self.is_root:
            return "FULL_PRIVILEGE_MODE"
        elif self.capabilities['system_commands'] and self.capabilities['process_management']:
            return "ENHANCED_USER_MODE"
        else:
            return "BASIC_USER_MODE"
