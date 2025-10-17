#!/usr/bin/env python3
"""
Monitor package manager changes (non-root)
"""
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_installed_packages():
    """
    Lists installed packages using the 'dpkg-query' command (Debian-based systems).
    This function does not require root privileges.
    Returns:
        A list of installed packages, or None if an error occurs.
    """
    try:
        result = subprocess.run(["dpkg-query", "-l"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            packages = result.stdout.strip().split('\n')
            # Remove header lines, leaving only package information
            packages = packages[5:]  # Skip header lines

            # Extract package names from the output
            package_names = [line.split()[1] for line in packages if len(line.split()) > 1]

            logger.info(f"[PACKAGE_MONITOR] Installed packages (dpkg-query): {package_names}")
            return package_names
        else:
            logger.warning("[PACKAGE_MONITOR] dpkg-query command failed. Cannot list installed packages.")
            return None
    except FileNotFoundError:
        logger.warning("[PACKAGE_MONITOR] dpkg-query command not found. This is likely not a Debian-based system.")
        return None
    except Exception as e:
        logger.exception(f"[PACKAGE_MONITOR] Error running dpkg-query: {e}")
        return None

def package_monitor():
    """
    Monitors installed packages using 'dpkg-query'.
    """
    packages = check_installed_packages()

    if packages:
        logger.info("[PACKAGE_MONITOR] Successfully checked installed packages.")
    else:
        logger.warning("[PACKAGE_MONITOR] Could not check installed packages.")

if __name__ == "__main__":
    package_monitor()
