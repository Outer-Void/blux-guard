#!/usr/bin/env python3
"""
Sensors Manager for BLUX Guard
- Runs all sensors concurrently
- Feeds events to trip_engine.py
- Termux/Linux compatible
"""

import os
import sys
import json
import threading
import queue
import time
import subprocess
from datetime import datetime

# Import sensor modules
from .sensors import network, dns, process_lifecycle, filesystem, permissions, hardware, human_factors

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIP_PY = os.path.join(REPO_ROOT, "security", "trip_engine.py")
PYTHON = os.environ.get("PYTHON", "python3")

# Queue to send events to trip_engine
event_queue = queue.Queue()

# ----------------------
# Event dispatcher
# ----------------------
def send_event(event):
    """Send a single JSON event to trip_engine.py via stdin."""
    if not os.path.isfile(TRIP_PY):
        print(f"[ERR] trip_engine.py not found at {TRIP_PY}", file=sys.stderr)
        return
    try:
        subprocess.run([PYTHON, TRIP_PY], input=json.dumps(event).encode("utf-8"), check=False)
    except Exception as e:
        print("[ERR] Failed to send event:", e)

def event_worker():
    """Consume events from queue and dispatch to trip_engine."""
    while True:
        event = event_queue.get()
        if event is None:
            break
        send_event(event)
        event_queue.task_done()

# ----------------------
# Sensor wrappers
# ----------------------
def wrap_sensor(fn, sensor_name):
    """Run a sensor's scan function in a loop and enqueue events."""
    while True:
        try:
            data = fn()
            event = {
                "sensor": sensor_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data": data
            }
            event_queue.put(event)
        except Exception as e:
            print(f"[ERR] {sensor_name} sensor failed: {e}", file=sys.stderr)
        time.sleep(5)  # default polling interval

# ----------------------
# Main manager
# ----------------------
def main():
    print("[INFO] Starting BLUX Guard Sensors Manager ...")

    # Start event dispatcher thread
    dispatcher = threading.Thread(target=event_worker, daemon=True)
    dispatcher.start()

    # Map sensors to their scan functions
    sensors = {
        "network": network.scan_flows,
        "dns": dns.capture_dns,
        "process_lifecycle": process_lifecycle.list_processes,
        "filesystem": filesystem.scan_files,
        "permissions": permissions.check_permissions,
        "hardware": lambda: {
            "charging": hardware.charging_status(),
            "bt_devices": hardware.bt_paired_devices(),
            "usb": hardware.usb_attached()
        },
        "human_factors": lambda: {
            "screen_locked": human_factors.screen_locked(),
            "user_present": human_factors.user_present()
        }
    }

    # Launch each sensor in its own thread
    threads = []
    for name, fn in sensors.items():
        t = threading.Thread(target=wrap_sensor, args=(fn, name), daemon=True)
        t.start()
        threads.append(t)
        print(f"[INFO] Sensor thread started: {name}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Shutting down sensors manager...")
    finally:
        # Stop event worker
        event_queue.put(None)
        dispatcher.join()
        print("[INFO] Sensors manager stopped.")

if __name__ == "__main__":
    main()