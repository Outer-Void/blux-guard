"""
BLUX Guard Anti-Tamper Package

This package provides tools for detecting tampering and unauthorized modifications
to the system.  It includes modules for monitoring su binaries, SELinux status,
and package manager changes.

Version: 1.0.0
Author: Outer Void Team
"""

import logging

# Configure logging (if not already configured elsewhere)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from .su_sentinel import su_sentinel, check_su_binaries, check_which_su
    SU_SENTINEL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"su_sentinel module not available: {e}")
    SU_SENTINEL_AVAILABLE = False

try:
    from .selinux_monitor import selinux_monitor, check_selinux, check_selinux_getenforce
    SELINUX_MONITOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"selinux_monitor module not available: {e}")
    SELINUX_MONITOR_AVAILABLE = False

try:
    from .package_monitor import package_monitor, check_installed_packages
    PACKAGE_MONITOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"package_monitor module not available: {e}")
    PACKAGE_MONITOR_AVAILABLE = False

__all__ = [
    "su_sentinel",  # if SU_SENTINEL_AVAILABLE else None,
    "check_su_binaries", # if SU_SENTINEL_AVAILABLE else None,
    "check_which_su", # if SU_SENTINEL_AVAILABLE else None,
    "selinux_monitor",  # if SELINUX_MONITOR_AVAILABLE else None,
    "check_selinux",  # if SELINUX_MONITOR_AVAILABLE else None,
    "check_selinux_getenforce",  # if SELINUX_MONITOR_AVAILABLE else None,
    "package_monitor",  # if PACKAGE_MONITOR_AVAILABLE else None,
    "check_installed_packages", # if PACKAGE_MONITOR_AVAILABLE else None,
    "SU_SENTINEL_AVAILABLE",
    "SELINUX_MONITOR_AVAILABLE",
    "PACKAGE_MONITOR_AVAILABLE",
    "logger",
]

# Remove None values from __all__ to prevent errors
__all__ = [item for item in __all__ if item is not None]
