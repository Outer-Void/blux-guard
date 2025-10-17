#!/usr/bin/env python3
"""
Anti-Tamper Engine
- Orchestrates nano-swarm, watchdog, and system integrity monitors
"""

import threading
from anti_tamper.watchdog import heartbeat
from anti_tamper import package_monitor, su_sentinel, selinux_monitor
from anti_tamper.nano_swarm import swarm_sim
import subprocess

def start_watchdog():
    t = threading.Thread(target=heartbeat.heartbeat, daemon=True)
    t.start()
    return t

def start_swarm():
    # Run swarm_sim in separate process (stdin loop optional)
    p = subprocess.Popen(["python3", swarm_sim.__file__])
    print(f"[ANTI-TAMPER] swarm started pid {p.pid}")
    return p

def monitor_integrity():
    package_monitor.check_packages()
    su_sentinel.check_su_binaries()
    selinux_monitor.check_selinux()

def main():
    wd_thread = start_watchdog()
    swarm_proc = start_swarm()

    try:
        while True:
            monitor_integrity()
            import time; time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down anti-tamper engine")
        swarm_proc.terminate()
        wd_thread.join(timeout=1)

if __name__ == "__main__":
    main()