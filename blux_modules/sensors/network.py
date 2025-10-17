"""
Network sensor: tracks flows and remote connections
"""

import time

def scan_flows():
    # Placeholder: replace with real flow inspection
    flows = [{"src":"10.0.0.1","dst":"8.8.8.8","bytes":1234}]
    print(f"[NETWORK] Flows detected: {flows}")
    return flows

def monitor_loop(interval=5):
    while True:
        scan_flows()
        time.sleep(interval)