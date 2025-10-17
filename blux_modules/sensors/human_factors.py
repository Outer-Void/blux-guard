"""
Human factors: unlock patterns, presence windows
"""

def screen_locked():
    locked = True
    print(f"[HUMAN] Screen locked: {locked}")
    return locked

def user_present():
    present = True
    print(f"[HUMAN] User present: {present}")
    return present

def monitor_loop(interval=5):
    import time
    while True:
        screen_locked()
        user_present()
        time.sleep(interval)