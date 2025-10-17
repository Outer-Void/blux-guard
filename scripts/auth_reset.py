#!/usr/bin/env python3
"""
BLUX Guard Auth Reset
Resets auth credentials if forgotten or in testing environment
USE WITH CAUTION - THIS REDUCES SECURITY
"""

import json
import getpass
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_reset")

def reset_auth():
    """Reset authentication credentials"""
    print("⚠️  AUTHENTICATION RESET TOOL")
    print("⚠️  USE ONLY IN TESTING OR IF CREDENTIALS ARE LOST")
    print("=" * 50)
    
    # Security confirmation
    response = input("Type 'RESET' to confirm auth reset: ")
    if response != "RESET":
        print("Reset cancelled.")
        return
    
    # Remove lock file
    lock_file = Path(".config/blux_guard/lock.hash")
    if lock_file.exists():
        lock_file.unlink()
        logger.info("Removed lock file")
    
    # Reset auth config
    auth_config = {
        "auth_method": "pin",
        "max_attempts": 3,
        "lockout_duration": 300,
        "require_auth_for": ["lockdown", "config_changes", "sensor_disable"],
        "pin_set": False
    }
    
    config_file = Path("config/auth.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(auth_config, f, indent=2)
    
    logger.info("Reset auth configuration")
    print("✅ Auth reset complete. Run set_user_pin.sh to set new credentials.")

if __name__ == "__main__":
    reset_auth()
