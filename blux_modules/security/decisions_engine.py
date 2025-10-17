#!/usr/bin/env python3
"""
BLUX Guard — Decision Layer Engine
- Escalation path: observe → intercept → quarantine → lockdown
- Uses UID policies from decision_layer/uid_policies.py
- Optional kill-switch for full isolation
"""

import os
from datetime import datetime
from security.decision_layer import uid_policies

# Paths
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KILL_SWITCH_FILE = os.path.join(REPO_ROOT, ".config", "blux-guard", "kill_switch.active")

ESCALATION_PATH = ["observe", "intercept", "quarantine", "lockdown"]

# Kill-switch
def kill_switch_active():
    return os.path.isfile(KILL_SWITCH_FILE)

def trigger_kill_switch():
    os.makedirs(os.path.dirname(KILL_SWITCH_FILE), exist_ok=True)
    with open(KILL_SWITCH_FILE, "w") as f:
        f.write(datetime.utcnow().isoformat() + "Z")
    print("[ALERT] Kill-switch triggered! System isolation active.")

def clear_kill_switch():
    if os.path.isfile(KILL_SWITCH_FILE):
        os.remove(KILL_SWITCH_FILE)
        print("[INFO] Kill-switch cleared.")

# Decision
def decide_action(event):
    if kill_switch_active():
        return "lockdown"

    uid = event.get("uid")
    policy = uid_policies.get_policy(uid)

    if policy == "whitelist":
        return "observe"
    elif policy == "greylist":
        severity = event.get("severity", 1)
        if severity >= 5:
            return "quarantine"
        elif severity >= 3:
            return "intercept"
        return "observe"
    elif policy == "blacklist":
        return "lockdown"
    return "observe"

def process_event(event):
    escalation = decide_action(event)
    result = {
        "uid": event.get("uid"),
        "escalation": escalation,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event
    }
    print(f"[DECISION] {result['uid']} -> {escalation}")
    return result

# Example usage
if __name__ == "__main__":
    test_events = [
        {"uid": "com.example.good", "severity": 1},
        {"uid": "com.example.suspicious", "severity": 4},
        {"uid": "com.example.malware", "severity": 6}
    ]
    for e in test_events:
        process_event(e)