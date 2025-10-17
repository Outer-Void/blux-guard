#!/usr/bin/env python3
"""
Detect su binaries or root escalation attempts
"""
import os
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_su_binaries():
    """
    Detects the presence of 'su' binaries in common system paths.
    Returns:
        A list of 'su' binaries found. If none are found returns an empty list.
    """
    paths = ["/system/bin/su", "/system/xbin/su", "/sbin/su", "/usr/bin/su", "/usr/local/bin/su"]
    found = [p for p in paths if os.path.exists(p)]
    if found:
        logger.warning(f"[SU_SENTINEL] su binaries found: {found}")
    return found

def check_which_su():
    """
    Uses the 'which su' command to attempt to locate 'su' binaries.
    This method does not require root privileges.
    Returns:
        A list of paths where 'su' binaries were found, or an empty list.
    """
    try:
        result = subprocess.run(["which", "su"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            paths = result.stdout.strip().split('\n')
            logger.warning(f"[SU_SENTINEL] 'which su' found: {paths}")
            return paths
        else:
            logger.info("[SU_SENTINEL] 'which su' did not find any su binaries.")
            return []
    except FileNotFoundError:
        logger.warning("[SU_SENTINEL] 'which' command not found. Cannot check for su binaries.")
        return []
    except Exception as e:
        logger.exception(f"[SU_SENTINEL] Error running 'which su': {e}")
        return []

def su_sentinel():
    """
    Checks for su binaries using both direct path checks and the 'which' command.
    """
    found_binaries = check_su_binaries()
    which_su_binaries = check_which_su()

    if found_binaries or which_su_binaries:
        all_found = found_binaries + which_su_binaries
        logger.warning(f"[SU_SENTINEL] Potential root escalation tools found: {all_found}")
    else:
        logger.info("[SU_SENTINEL] No su binaries found.")

if __name__ == "__main__":
    su_sentinel()
