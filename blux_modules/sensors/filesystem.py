"""
Filesystem sensor: monitor file creation/modification
"""

import os
import time

WATCH_DIR = "/tmp"  # placeholder

def scan_files():
    files = os.listdir(WATCH_DIR)
    print(f"[FS] Files in {WATCH_DIR}: {files[:5]} ...")
    return files

def monitor_loop(interval=5):
    while True:
        scan_files()
        time.sleep(interval)