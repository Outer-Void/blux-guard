"""
Permissions sensor: track changes in file or app permissions
"""

import os

def check_permissions(path="/tmp"):
    for f in os.listdir(path)[:5]:
        full = os.path.join(path, f)
        perms = oct(os.stat(full).st_mode)[-3:]
        print(f"[PERM] {f}: {perms}")

def monitor_loop(interval=5):
    import time
    while True:
        check_permissions()
        time.sleep(interval)