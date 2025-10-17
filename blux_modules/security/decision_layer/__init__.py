"""
BLUX Guard Decision Layer Package

This package provides the decision-making logic for the BLUX Guard system,
allowing it to respond intelligently to security events based on predefined
policies.

Version: 1.0.0
Author: Outer Void Team
"""

import logging

# Configure logging (if not already configured elsewhere)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from .uuid_policies import get_policy, load_uid_policies #DEFAULT_POLICY # import what is needed
    UUID_POLICIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"uuid_policies module not available: {e}")
    UUID_POLICIES_AVAILABLE = False

__all__ = [
    "get_policy",  # if UUID_POLICIES_AVAILABLE else None,
    "load_uid_policies", # if UUID_POLICIES_AVAILABLE else None,
    # "DEFAULT_POLICY", # if UUID_POLICIES_AVAILABLE else None,
    "UUID_POLICIES_AVAILABLE",
    "logger",
]

# Remove None values from __all__ to prevent errors
__all__ = [item for item in __all__ if item is not None]
