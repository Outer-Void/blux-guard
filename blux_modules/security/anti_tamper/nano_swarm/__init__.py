"""
BLUX Guard Nano-Swarm Anti-Tamper Package

This package provides a system of internal, defensive agents that act as an
early warning system against unauthorized modifications or intrusions.  It
incorporates YARA-based malware detection and can be extended with other
anti-tamper techniques.

Version: 1.0.0
Author: Outer Void Team
"""

import os
import logging

# Configure logging (if not already configured elsewhere)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the main nano-swarm module (replace with actual module name)
try:
    from .swarm_sim import main, Agent, ApkWatchHandler, SwarmApp # adapt import to filename and classes
    NANO_SWARM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Nano-swarm module not available: {e}")
    NANO_SWARM_AVAILABLE = False

# Import any other relevant modules or functions (e.g., configuration classes)
# from .config import NanoSwarmConfig

# Define __all__ to control the public API of the package
__all__ = [
    "main",  # if NANO_SWARM_AVAILABLE else None,  # Only expose if available
    "Agent", # if NANO_SWARM_AVAILABLE else None,
    "ApkWatchHandler", # if NANO_SWARM_AVAILABLE else None,
    "SwarmApp", # if NANO_SWARM_AVAILABLE else None,
    # "NanoSwarmConfig", # Uncomment if you have a config class
    "NANO_SWARM_AVAILABLE",
    "logger", # Always expose the logger
]

# Remove None values from __all__ to prevent errors
__all__ = [item for item in __all__ if item is not None]
