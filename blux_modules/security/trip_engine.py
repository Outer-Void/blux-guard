#!/usr/bin/env python3
"""
BLUX Guard – Trip Engine demo (Termux-friendly)

Structure-aware version for ~/blux-guard layout:

  .config/blux-guard/        → runtime configs, key
  .config/rules/rules.json   → signed trip rules
  security/logs/             → append-only incidents.log

Usage:
  echo '{"uid":"com.example","network":{"remote_ips_count":80}}' | python security/trip_engine.py

Outputs:
  - Compact alert: <base64(payload)>.<base64(hmac)> (stdout)
  - Append-only signed incident line (security/logs/incidents.log)
  - “OK” when no rule triggers
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
from collections import defaultdict, deque

# === Path Configuration ===

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(ROOT_DIR, ".config", "blux-guard")
RULES_PATH = os.path.join(ROOT_DIR, ".config", "rules", "rules.json")
KEY_PATH = os.path.join(CONFIG_DIR, "key")
LOGS_DIR = os.path.join(ROOT_DIR, "security", "logs")
INCIDENTS_PATH = os.path.join(LOGS_DIR, "incidents.log")

# Ensure dirs
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# === Key Management ===

def load_or_create_key(path=KEY_PATH):
    """Generate or load symmetric HMAC-SHA256 key (demo purpose only)."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    k = hashlib.sha256(str(time.time()).encode() + os.urandom(32)).digest()
    with open(path, "wb") as f:
        f.write(k)
    os.chmod(path, 0o600)
    return k

KEY = load_or_create_key()

# === JSON + Crypto helpers ===

def canonical_json(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")

def hmac_sign(b):
    mac = hmac.new(KEY, b, hashlib.sha256).digest()
    return base64.b64encode(mac).decode()

def compact_alert(payload_obj):
    b = canonical_json(payload_obj)
    sig = hmac_sign(b)
    return base64.b64encode(b).decode() + "." + sig

# === Rule Loading ===

def load_rules(path=RULES_PATH):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    print(f"[WARN] Rules not found at {path}.", file=sys.stderr)
    return {"rules": []}

RULESET = load_rules()

# === In-memory state ===

WINDOWS = defaultdict(lambda: defaultdict(deque))

def get_field(event, path):
    cur = event
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

# === Condition Evaluation ===

def eval_condition(cond, event, now_ts):
    t = cond.get("type")
    if t == "threshold":
        field = cond["field"]
        op = cond.get("op", "gt")
        value = cond["value"]
        window_s = cond.get("window", 60)
        uid = event.get("uid", "<unknown>")
        dq = WINDOWS[uid][field]
        field_val = get_field(event, field)
        if isinstance(field_val, (int, float)) and field_val:
            dq.append(now_ts)
        elif field_val:
            dq.append(now_ts)
        cutoff = now_ts - window_s
        while dq and dq[0] < cutoff:
            dq.popleft()
        count = len(dq)
        return {
            "gt": count > value,
            "gte": count >= value,
            "eq": count == value,
            "lt": count < value,
            "lte": count <= value,
        }.get(op, False)

    elif t == "match":
        return get_field(event, cond["field"]) == cond.get("value")

    elif t == "exists":
        return get_field(event, cond["field"]) is not None

    elif t == "and":
        return all(eval_condition(c, event, now_ts) for c in cond.get("clauses", []))

    elif t == "or":
        return any(eval_condition(c, event, now_ts) for c in cond.get("clauses", []))

    return False

# === Incident Handling ===

def make_incident(rule, event, now_ts, extra=None):
    return {
        "rule_id": rule.get("id"),
        "rule_name": rule.get("name"),
        "timestamp": int(now_ts),
        "uid": event.get("uid"),
        "event_snapshot": event,
        "meta": extra or {},
    }

def append_incident_log(inc):
    b = canonical_json(inc)
    sig = hmac.new(KEY, b, hashlib.sha256).hexdigest()
    line = b.decode() + "  " + sig + "\n"
    with open(INCIDENTS_PATH, "a") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())

# === Main loop ===

def process_event(event):
    now_ts = time.time()
    triggered = []
    for rule in RULESET.get("rules", []):
        cond = rule.get("condition")
        if not cond:
            continue
        try:
            hit = eval_condition(cond, event, now_ts)
        except Exception as e:
            print(f"[ERR] Rule {rule.get('id')} error: {e}", file=sys.stderr)
            hit = False
        if hit:
            triggered.append(rule)
            inc = make_incident(rule, event, now_ts, {"note": "rule_triggered"})
            append_incident_log(inc)
            print(compact_alert(inc), flush=True)
    if not triggered:
        print("OK", flush=True)
    return triggered

def repl_stdin_loop():
    print("[Trip Engine] ready — feed JSON events on stdin.", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except Exception as e:
            print("[WARN] Invalid JSON:", e, file=sys.stderr)
            continue
        process_event(evt)

# === Entrypoint ===

if __name__ == "__main__":
    print("[Trip Engine] starting...", file=sys.stderr)
    print(f"Rules loaded: {len(RULESET.get('rules', []))}", file=sys.stderr)
    print(f"Incidents log: {INCIDENTS_PATH}", file=sys.stderr)
    repl_stdin_loop()= compact_alert(inc)
            print(alert, flush=True)
    return triggered

def repl_stdin_loop():
    print("Trip Engine demo: ready. Feed JSON events (one per line) via stdin.", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except Exception as e:
            print("Invalid JSON (skipping):", e, file=sys.stderr)
            continue
        triggered = process_event(evt)
        if not triggered:
            # For demo, also echo "OK" so a caller sees that no trip happened
            print("OK", flush=True)

if __name__ == "__main__":
    # on startup, print summary
    print("Trip Engine demo starting...", file=sys.stderr)
    print(f"Rules loaded: {len(RULESET.get('rules', []))}", file=sys.stderr)
    print(f"Incidents file: {INCIDENTS_PATH}", file=sys.stderr)
    repl_stdin_loop()