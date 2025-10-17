"""
BLUX Guard Containment and Response Package

This package provides tools for containing and responding to security incidents,
including process isolation, network interception, incident logging, and
filesystem containment.

Version: 1.0.0
Author: Outer Void Team
"""

import logging

# Configure logging (if not already configured elsewhere)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from .process_isolater import isolate_process, snapshot_process, rollback_process # Add needed items
    PROCESS_ISOLATER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"process_isolater module not available: {e}")
    PROCESS_ISOLATER_AVAILABLE = False

try:
    from .network_interceptor import intercept_network
    NETWORK_INTERCEPTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"network_interceptor module not available: {e}")
    NETWORK_INTERCEPTOR_AVAILABLE = False

try:
    from .logging import log_incident
    LOGGING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"logging module not available: {e}")
    LOGGING_AVAILABLE = False

try:
    from .filesystem import quarantine_path, revert_permissions, ui_fuse
    FILESYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"filesystem module not available: {e}")
    FILESYSTEM_AVAILABLE = False

__all__ = [
    "isolate_process",  # if PROCESS_ISOLATER_AVAILABLE else None,
    "snapshot_process", # if PROCESS_ISOLATER_AVAILABLE else None,
    "rollback_process", # if PROCESS_ISOLATER_AVAILABLE else None,
    "intercept_network",  # if NETWORK_INTERCEPTOR_AVAILABLE else None,
    "log_incident",  # if LOGGING_AVAILABLE else None,
    "quarantine_path",  # if FILESYSTEM_AVAILABLE else None,
    "revert_permissions", # if FILESYSTEM_AVAILABLE else None,
    "ui_fuse",  # if FILESYSTEM_AVAILABLE else None,
    "PROCESS_ISOLATER_AVAILABLE",
    "NETWORK_INTERCEPTOR_AVAILABLE",
    "LOGGING_AVAILABLE",
    "FILESYSTEM_AVAILABLE",
    "logger",
]

# Remove None values from __all__ to prevent errors
__all__ = [item for item in __all__ if item is not None]
