#!/usr/bin/env python3
"""
BLUX Guard — Signed incident logging
- All events signed & timestamped
- Stored in security/logs/
"""

import os
import json
import logging
from datetime import datetime
from hashlib import sha256

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define default logs directory relative to the script's location.
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
INCIDENTS = os.path.join(LOGS_DIR, "incidents.log")

def log_incident(event: dict):
    """Logs an incident with a timestamp and signature."""
    # Sanitize the event dict of any non-serializable data.
    try:
        event_copy = event.copy()
        event_copy["timestamp"] = datetime.utcnow().isoformat() + "Z"
        serialized = json.dumps(event_copy, sort_keys=True, default=str)
        # Simple hash signature
        signature = sha256(serialized.encode()).hexdigest()
        entry = {"event": event_copy, "signature": signature}
        # Ensure the directory exists.
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(INCIDENTS, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        logger.info(f"[LOGGED] UID={event.get('uid')} signature={signature}")
        return entry
    except Exception as e:
        logger.exception(f"[LOGGING] Error logging incident: {e}")
        return None

if __name__ == "__main__":
    # Example Usage:
    test_event = {"uid": 1000, "message": "Suspicious activity detected."}
    log_incident(test_event)
