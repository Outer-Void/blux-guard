#!/usr/bin/env python3
"""
Watchdog self-heartbeat and process monitor
- Periodically checks core files & process state
- Can restart anti-tamper engines if they fail
"""

import time
import os
import sys
import logging
import subprocess
from pathlib import Path

# Third-party library imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available. Please install with 'pip install psutil'")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---- Configuration (Environment Variables) ----
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "5"))  # seconds
WATCH_FILES = os.environ.get("WATCH_FILES", "").split(",")  # Comma-separated list of file paths
WATCH_PROCESSES = os.environ.get("WATCH_PROCESSES", "").split(",")  # Comma-separated list of process names
RESTART_SCRIPT = os.environ.get("RESTART_SCRIPT", "") # Path to restart script

def check_dependencies():
    """Checks if dependencies are available"""
    # psutil Dependency Check
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil not available. Some functionalities will be disabled")
        return False

def heartbeat():
    """
    Main heartbeat function that monitors files and processes.
    """
    logger.info("Watchdog heartbeat started")
    while True:
        # Check for missing files
        for f in WATCH_FILES:
            f = f.strip()  # Remove whitespace
            if not f:
                continue # Skip empty entries
            try:
                if not Path(f).exists():
                    logger.error(f"[WATCHDOG] MISSING {f}")
            except Exception as e:
                logger.exception(f"[WATCHDOG] Error checking file {f}: {e}")

        # Check if processes are running
        for proc_name in WATCH_PROCESSES:
            proc_name = proc_name.strip()  # Remove whitespace
            if not proc_name:
                continue # Skip empty entries
            try:
                process_running = False
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == proc_name:
                        process_running = True
                        break

                if not process_running:
                    logger.error(f"[WATCHDOG] Process NOT RUNNING: {proc_name}")
                    if RESTART_SCRIPT:
                        logger.info(f"[WATCHDOG] Attempting restart using: {RESTART_SCRIPT}")
                        try:
                            # Execute restart script
                            subprocess.run([RESTART_SCRIPT], check=True, shell=False, capture_output=True, text=True)
                            logger.info(f"[WATCHDOG] Process {proc_name} restarted.")
                        except subprocess.CalledProcessError as e:
                            logger.error(f"[WATCHDOG] Failed to restart {proc_name}: {e.stderr}")
                        except Exception as e:
                            logger.exception(f"[WATCHDOG] Error restarting {proc_name}: {e}")
                    else:
                        logger.warning(f"[WATCHDOG] No RESTART_SCRIPT defined.")
                else:
                    logger.info(f"[WATCHDOG] Process RUNNING: {proc_name}")

            except Exception as e:
                logger.exception(f"[WATCHDOG] Error checking process {proc_name}: {e}")

        logger.info("[WATCHDOG] Heartbeat OK")
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    if check_dependencies() != False:
        heartbeat()
    else:
        logger.error("Dependency Error: check the logs, exiting")
