"""
Process lifecycle sensor: track start/stop of processes
"""

import os
import time

def list_processes():
    # Placeholder: just list current PIDs
    pids = [pid for pid in os.listdir("/proc") if pid.isdigit()]
    print(f"[PROC] Active PIDs: {pids[:5]} ...")
    return pids

def monitor_loop(interval=5):
    while True:
        list_processes()
        time.sleep(interval)