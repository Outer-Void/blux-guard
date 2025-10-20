# BLUX Guard

> Android Terminal High-Alert Security System

---

## Vision

A discreet, layered defender that uses deterministic trip-variables, tamper-resistant sensors, and safe containment to protect **your own devices** — transparent, auditable, and always under operator control.

---

## Directory Layout

```bash
blux-guard/
├── blux_cli/
│   ├── blux.py
│   ├── __init__.py
│   ├── security_integration.py
│   └── widgets/
│       ├── anti_tamper_controls.py
│       ├── blux_cockpit.css
│       ├── cockpit_header_footer.py
│       ├── decisions_view.py
│       ├── dev_menu_tree.py
│       ├── __init__.py
│       ├── logs_view.py
│       ├── network_monitor.py
│       ├── node_data.json
│       ├── process_monitor.py
│       ├── scripts_view.py
│       ├── sensors_dashboard.py
│       └── tree.py
├── blux_guard_shell/
│   ├── __init__.py
│   └── shell_menu.py
├── blux_modules/
│   ├── __init__.py
│   ├── security/
│   │   ├── anti_tamper/
│   │   │   ├── __init__.py
│   │   │   ├── nano_swarm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── swarm.css
│   │   │   │   └── swarm_sim.py
│   │   │   ├── package_monitor.py
│   │   │   ├── selinux_monitor.py
│   │   │   ├── su_sentinel.py
│   │   │   └── watchdog/
│   │   │       ├── heartbeat.py
│   │   │       └── __init__.py
│   │   ├── anti_tamper_engine.py
│   │   ├── auth_system.py
│   │   ├── contain_engine.py
│   │   ├── contain_respond/
│   │   │   ├── filesystem.py
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   └── network_intercepter.py
│   │   ├── decision_layer/
│   │   │   ├── __init__.py
│   │   │   ├── policies.json
│   │   │   ├── policies.txt
│   │   │   └── uid_policies.py
│   │   ├── decisions_engine.py
│   │   ├── __init__.py
│   │   ├── privilege_manager.py
│   │   ├── sensors_manager.py
│   │   └── trip_engine.py
│   └── sensors/
│       ├── dns.py
│       ├── filesystem.py
│       ├── hardware.py
│       ├── human_factors.py
│       ├── __init__.py
│       ├── network.py
│       ├── permission.py
│       ├── permissions.py
│       └── process_lifecycle.py
├── blux_shell.py
├── initiate_cockpit.py
├── logs/
│   ├── anti_tamper/
│   ├── decisions/
│   │   └── incidents.log
│   └── sensors/
├── pyproject.toml
├── README.md
├── requirements.txt
└── scripts/
    ├── auth_reset.py
    ├── check_root.sh
    ├── check_status.sh
    ├── clean_temp.sh
    ├── create_venv.sh
    ├── daily_report.sh
    ├── debug_env.sh
    ├── initiate_cockpit.sh
    ├── __init__.py
    ├── inspect_modules.py
    ├── reload_config.sh
    ├── restart.sh
    ├── root_workaround.sh
    ├── rotate_logs.sh
    ├── run_guard.sh
    ├── schedule_checks.sh
    ├── setup_env.sh
    ├── setup_security.py
    ├── set_user_pin.sh
    ├── unlock_system.sh
    └── update_modules.sh

21 directories, 114 files
```

---

## 1. Architecture Overview

Sensors → Trip Engine → Decision Layer → Containment → Operator

1.1 Sensors (Data Sources)

· Network flows, DNS queries, process lifecycle
· Filesystem changes, permission modifications
· Hardware events: charging, BT pairing, USB attach
· Human factors: unlock patterns, presence windows

1.2 Trip Engine (Deterministic Rules)

· Boolean and temporal trip-wires
· Thresholded counters and state chains
· Signed, versioned rule manifests in .config/rules/rules.json

1.3 Decision Layer

· Escalation path: observe → intercept → quarantine → lockdown
· Per-UID policies: whitelist / greylist / blacklist
· Optional kill-switch for complete isolation

1.4 Containment & Response

· Network interceptor (VpnService-like)
· Process isolator / snapshot & rollback
· Filesystem quarantine, permission reverter, UI fuse
· Signed incident logs in logs/decisions/incidents.log

1.5 Integrity & Anti-tamper

· Watchdog with self-heartbeat
· Signed binaries & manifests
· Alerts on package manager, su binaries, SELinux changes

---

## 2. Core Components

2.1 Security Modules (blux_modules/security/)

· auth_system.py - Authentication and password management
· privilege_manager.py - Root detection and privilege escalation
· trip_engine.py - Rule evaluation and incident detection
· decisions_engine.py - Action escalation and policy enforcement
· anti_tamper_engine.py - System integrity monitoring
· sensors_manager.py - Unified sensor data collection

2.2 Sensor Suite (blux_modules/sensors/)

· network.py - Network connection monitoring
· dns.py - DNS query analysis
· process_lifecycle.py - Process tracking
· filesystem.py - File system monitoring
· hardware.py - USB/BT/charging detection
· human_factors.py - User behavior analysis
· permission.py - Permission change detection

2.3 User Interfaces

· blux_guard_shell/ - Interactive shell menu system
· blux_cli/ - Command-line interface with TUI widgets
· initiate_cockpit.py - Graphical cockpit interface
· blux_shell.py - Shell launcher wrapper

2.4 Anti-Tamper System (blux_modules/security/anti_tamper/)

· nano_swarm/ - Distributed security monitoring
· watchdog/ - System heartbeat and integrity checks
· package_monitor.py - Package manager surveillance
· selinux_monitor.py - SELinux policy monitoring
· su_sentinel.py - Root access detection

---

## 3. Quick Start

3.1 Installation

```bash
# Clone the repository
git clone https://github.com/Outer-Void/blux-guard.git
cd blux-guard

# Install dependencies
pip install -r requirements.txt
```

3.2 First Run

```bash
# Start with the interactive shell
python3 blux_guard_shell/shell_menu.py

# Or use the graphical cockpit
python3 initiate_cockpit.py

# Or use the CLI
python3 blux_cli/blux.py status
```

3.3 Authentication

· First run will prompt for PIN setup
· Use the same PIN across all interfaces
· Emergency reset available via shell menu

---

## 4. Trip Engine Examples

Deterministic, time-bounded, and auditable

Scenario Trip Condition Action
Silent Exfil 10 external sockets to distinct IPs in 60s Block, snapshot, notify
Mount Surprise SD mounted while locked & charging & idle 12h+ Read-only + checksum
Privilege Creep New permission soon after unknown net conn Revert + quarantine
Process Mimic Same pkg name, different cert/hash Freeze + capture
UI Hijack Overlay within 2s of credential event Block overlay + prompt
Cold-start Lateral Unknown AUTOSTART after reboot Block autostart until review

---

## 5. AI Security Plan

Principle: Break hostile AI effectiveness by destroying input reliability and computation economics.

Strategy I — "Pull It Apart"

· Deterministic jitter to break time-series features
· Proof-of-Work throttles (per-UID PoW)
· Honeypots and deceptive metadata
· Never auto-confirm success — require human validation

Strategy II — "EMP Metaphor"

· Circuit breakers to air-gap radios or network routes
· Freeze/snapshot suspect processes
· Reduce CPU/QoS for suspect UIDs
· All actions signed and operator-approved

---

## 6. Operational Scripts

The scripts/ directory contains utilities for:

· Security setup: setup_security.py, set_user_pin.sh
· System maintenance: rotate_logs.sh, clean_temp.sh
· Debugging: debug_env.sh, inspect_modules.py
· Automation: daily_report.sh, schedule_checks.sh

---

## 7. Governance & Ethics

Defensive-only. No offensive payloads. All commits and rule changes must include:

· Author signature
· Simulation or test logs
· One reviewer sign-off

Security Protocols:

· Private signing keys must never reside on the same device
· Critical changes require physical ACK (BLE/NFC or manual gesture)
· Maintain an auditable signed changelog

---

## 8. Roadmap

Stage Goal
v0.1 Termux Trip Engine prototype
v0.2 Honeypot + canary endpoint
v0.3 BLE companion listener
v0.4 Kotlin VpnService interceptor
v0.5 Consensus agent coordinator
v1.0 Full BLUX Guard operator suite

---

## 9. Legal & Safety

· ✅ Works only on devices you own or control
· ✅ Forensics data remains private and encrypted
· ✅ Always test on secondary hardware first
· ✅ Never modify or erase evidence automatically

---

## Getting Help

· Check individual module docstrings for usage
· Review scripts/ for operational utilities
· Use the interactive shell for guided operation

BLUX Guard Doctrine — Building walls that respect your hunger and deny the pack.


