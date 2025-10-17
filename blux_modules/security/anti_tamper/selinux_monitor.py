#!/usr/bin/env python3
"""
Monitor SELinux mode changes
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_selinux():
    """
    Checks the SELinux enforcement mode by reading the /sys/fs/selinux/enforce file.
    Note: This function requires root privileges to read the file.
    Returns:
        The SELinux enforcement mode ('0' for permissive, '1' for enforcing),
        or None if SELinux is not available or an error occurs.
    """
    try:
        with open("/sys/fs/selinux/enforce") as f:
            enforce = f.read().strip()
        logger.info(f"[SELINUX] enforce={enforce}")
        return enforce
    except FileNotFoundError:
        logger.info("[SELINUX] Not available")
        return None
    except PermissionError:
        logger.warning("[SELINUX] Permission denied to read /sys/fs/selinux/enforce. Requires root.")
        return None
    except Exception as e:
        logger.exception(f"[SELINUX] Error checking SELinux status: {e}")
        return None

def check_selinux_getenforce():
    """
    Checks SELinux enforcement status using the 'getenforce' command.
    This function does not require root privileges and may provide SELinux status.
    Returns:
        The SELinux enforcement status ('Enforcing' or 'Permissive'), or None if not available or an error occurs.
    """
    try:
        result = subprocess.run(["getenforce"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            enforce_status = result.stdout.strip()
            logger.info(f"[SELINUX] getenforce status: {enforce_status}")
            return enforce_status
        else:
            logger.info("[SELINUX] getenforce command failed. SELinux status may not be available.")
            return None
    except FileNotFoundError:
        logger.warning("[SELINUX] getenforce command not found. Cannot check SELinux status.")
        return None
    except Exception as e:
        logger.exception(f"[SELINUX] Error running getenforce: {e}")
        return None

def selinux_monitor():
    """
    Monitors the SELinux status using both direct file checks (requires root) and the 'getenforce' command.
    """
    file_enforce = check_selinux()
    getenforce_status = check_selinux_getenforce()

    if file_enforce:
        logger.info(f"[SELINUX] File-based SELinux status: {file_enforce}")
    if getenforce_status:
        logger.info(f"[SELINUX] getenforce-based SELinux status: {getenforce_status}")

    if not file_enforce and not getenforce_status:
        logger.info("[SELINUX] Could not determine SELinux status.")

if __name__ == "__main__":
    selinux_monitor()
