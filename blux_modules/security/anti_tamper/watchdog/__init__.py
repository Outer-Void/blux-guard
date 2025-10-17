"""
BLUX Guard Watchdog Package

This package provides a heartbeat mechanism to monitor critical files and
processes, ensuring the integrity and availability of the system.

Version: 1.0.0
Author: Outer Void Team
"""

import logging

# Configure logging (if not already configured elsewhere)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from .heartbeat import heartbeat # Import heartbeat function
    WATCHDOG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Watchdog module not available: {e}")
    WATCHDOG_AVAILABLE = False

# Define __all__ to control the public API of the package
__all__ = [
    "heartbeat",  # if WATCHDOG_AVAILABLE else None,  # Only expose if available
    "WATCHDOG_AVAILABLE",
    "logger", # Always expose the logger
]

# Remove None values from __all__ to prevent errors
__all__ = [item for item in __all__ if item is not None]
