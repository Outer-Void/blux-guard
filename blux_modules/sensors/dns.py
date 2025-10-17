"""
DNS sensor: monitors queries/resolutions
"""

import time

def capture_dns():
    # Placeholder: simulate a DNS query log
    queries = ["example.com", "bad.site"]
    print(f"[DNS] Captured DNS queries: {queries}")
    return queries

def monitor_loop(interval=5):
    while True:
        capture_dns()
        time.sleep(interval)