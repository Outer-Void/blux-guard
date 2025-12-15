# BLUX Guard

> Android Terminal High-Alert Security System

---

## Vision

A discreet, layered defender that uses deterministic trip-variables, tamper-resistant sensors, and safe containment to protect **your own devices** — transparent, auditable, and always under operator control.

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

### Unified Operator Flow

```bash
# Preferred cockpit launch (Textual)
python -m blux_guard.cli.bluxq guard tui

# Quick health checks
python -m blux_guard.cli.bluxq guard status
python -m blux_guard.cli.bluxq guard doctor

# Export telemetry snapshot
python -m blux_guard.cli.bluxq guard export
```

Legacy entry points remain available, but the `bluxq guard` namespace is the single supported path that propagates correlation IDs, writes unified audit JSONL entries, and exposes the DevShell panel.

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

Run the top-level helpers to keep these scripts healthy and executable:

```
make perms          # normalize executable bits from scripts/perms_manifest.txt
make audit-scripts  # verify shebangs, CRLF, and manifest coverage
make smoke          # light import + CLI smoke checks (includes audit-scripts)
```

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



---

## Power Mode 2.0 Quick Start

1. **Install**
   ```bash
   # recommended virtual environment
   python -m pip install -U pip
   pip install -e .
   ```
2. **Launch the daemon and cockpit**
   ```bash
   bluxqd &
   bluxq guard status
   bluxq guard tui --mode dev
   ```
3. **Developer workflows**
   ```bash
   bluxq dev init
   bluxq dev shell
   bluxq dev scan .
   bluxq dev deploy --safe
   ```
4. **Fallbacks** — `initiate_cockpit.py` and the legacy CLI continue to operate unchanged.

## Security Model & Doctrine Alignment

- **User / Operator / Root (cA)** tiers remain enforced. Developer flows inherit doctrine checks before privileged actions.
- All automation routes through the sandboxed PTY shell to respect containment boundaries.
- Doctrine integrations surface alignment scores directly inside the cockpit and via the CLI.

## Telemetry & Reliability

BLUX Guard writes best-effort logs to:

- `~/.config/blux-guard/logs/audit.jsonl`
- `~/.config/blux-guard/logs/devshell.jsonl` (developer shell stream)
- Optional mirror: `~/.config/blux-guard/logs/telemetry.db` (SQLite)

If the directory is unwritable or SQLite is unavailable, logging **degrades silently** and the app **continues running**.

Toggles:

- `BLUX_GUARD_TELEMETRY=off` → disable telemetry writes
- `BLUX_GUARD_TELEMETRY_WARN=once` → show a single degrade warning on stderr

## Cross-Platform Notes

- **Android / Termux** – installers configure aliases; telemetry lives under `$HOME/.config/blux-guard/logs`.
- **WSL2 & Linux** – sandbox shell defaults to `/bin/bash`, Prometheus metrics export via `bluxqd`.
- **macOS** – shell panel launches `/bin/zsh` while retaining doctrine validation.
- **Windows** – PowerShell support via `COMSPEC`; telemetry paths expand to `%USERPROFILE%\.config\blux-guard\logs`.

## Troubleshooting

- **CLI reports `ModuleNotFoundError: typer`** – reinstall with `pip install -e .` to ensure dependencies.
- **Permission denied writing logs** – create the telemetry directory manually or set `BLUX_GUARD_TELEMETRY=off`.
- **SQLite locked or missing** – mirror is optional; the CLI continues using JSONL streams and emits a single degrade warning when enabled.
- **Termux storage prompts** – run `termux-setup-storage` before launching to grant write access.

BLUX Guard — the forge remains open, even when the pen runs dry.

## Developer Suite Quick Start

```bash
# Install (venv recommended)
python -m pip install -U pip
pip install -e .

# Start daemon & open cockpit
bluxqd &
bluxq guard status
bluxq guard tui --mode dev
```

Telemetry is best-effort:

- JSONL: `~/.config/blux-guard/logs/audit.jsonl`
- Dev shell: `~/.config/blux-guard/logs/devshell.jsonl`
- SQLite mirror (optional): `~/.config/blux-guard/logs/telemetry.db`

To disable: `BLUX_GUARD_TELEMETRY=off`.

## Documentation Map

- [ARCHITECTURE.md](ARCHITECTURE.md) — module graph and platform matrix.
- [INSTALL.md](INSTALL.md) — platform-specific install steps.
- [OPERATIONS.md](OPERATIONS.md) — runbook for day-two operations.
- [SECURITY.md](SECURITY.md) — threat model, doctrine enforcement, telemetry guarantees.
- [PRIVACY.md](PRIVACY.md) — telemetry scope and retention controls.
- [CONFIGURATION.md](CONFIGURATION.md) — YAML schema and overrides.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — quick fixes for common issues.
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution workflow and coding standards.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community expectations.
- [SUPPORT.md](SUPPORT.md) — escalation paths and SLAs.
- [ROADMAP.md](ROADMAP.md) — upcoming milestones.

## Supported Python Versions

The cockpit validates Python 3.9+ on startup. Supported interpreters: 3.9, 3.10, and 3.11. Upgrade the
interpreter if you receive a startup warning.

## Licensing

Blux Guard is dual-licensed. Open-source use is provided under the [Apache License 2.0](LICENSE-APACHE), and commercial use requires a separate agreement described in [LICENSE-COMMERCIAL](LICENSE-COMMERCIAL).

Under Apache-2.0 you may use, modify, and redistribute the software for open and internal purposes, provided that you preserve notices, include the license, and accept the standard disclaimers of warranty and liability.

Commercial use—such as embedding in paid products, offering hosted services, or other monetized deployments—requires a commercial license from the maintainers. Please review [COMMERCIAL.md](COMMERCIAL.md) for examples and contact **theoutervoid@outlook.com** to arrange commercial terms.

<!-- FILETREE:BEGIN -->
<!-- generated; do not edit manually -->
<details><summary><strong>Repository File Tree</strong> (click to expand)</summary>

```text
blux-guard/
├── .github
│   ├── workflows
│   │   ├── ci.yml
│   │   └── security.yml
│   └── dependabot.yml
├── blux_cli
│   ├── widgets
│   │   ├── __init__.py
│   │   ├── anti_tamper_controls.py
│   │   ├── blux_cockpit.css
│   │   ├── cockpit_header_footer.py
│   │   ├── decisions_view.py
│   │   ├── dev_menu_tree.py
│   │   ├── logs_view.py
│   │   ├── network_monitor.py
│   │   ├── node_data.json
│   │   ├── process_monitor.py
│   │   ├── scripts_view.py
│   │   ├── sensors_dashboard.py
│   │   └── tree.py
│   ├── __init__.py
│   ├── blux.py
│   └── security_integration.py
├── blux_guard
│   ├── agents
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── linux_agent.py
│   │   ├── mac_agent.py
│   │   ├── termux_agent.py
│   │   └── windows_agent.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── guardd.py
│   │   ├── server.py
│   │   └── stream.py
│   ├── cli
│   │   ├── __init__.py
│   │   ├── bluxq.py
│   │   └── README.md
│   ├── config
│   │   ├── __init__.py
│   │   ├── default.yaml
│   │   └── local.yaml
│   ├── core
│   │   ├── __init__.py
│   │   ├── devsuite.py
│   │   ├── doctrine_integration.py
│   │   ├── engine.py
│   │   ├── runtime.py
│   │   ├── sandbox.py
│   │   ├── selfcheck.py
│   │   ├── telemetry.md
│   │   └── telemetry.py
│   ├── tui
│   │   ├── __init__.py
│   │   ├── audit_panel.py
│   │   ├── dashboard.py
│   │   ├── metrics_panel.py
│   │   ├── README.md
│   │   └── shell_panel.py
│   └── __init__.py
├── blux_guard_shell
│   ├── __init__.py
│   └── shell_menu.py
├── blux_modules
│   ├── security
│   │   ├── anti_tamper
│   │   │   ├── nano_swarm
│   │   │   │   ├── __init__.py
│   │   │   │   ├── swarm.css
│   │   │   │   └── swarm_sim.py
│   │   │   ├── watchdog
│   │   │   │   ├── __init__.py
│   │   │   │   └── heartbeat.py
│   │   │   ├── __init__.py
│   │   │   ├── package_monitor.py
│   │   │   ├── selinux_monitor.py
│   │   │   └── su_sentinel.py
│   │   ├── contain_respond
│   │   │   ├── __init__.py
│   │   │   ├── filesystem.py
│   │   │   ├── logging.py
│   │   │   ├── network_intercepter.py
│   │   │   └── process_isolator.py
│   │   ├── decision_layer
│   │   │   ├── __init__.py
│   │   │   ├── policies.json
│   │   │   ├── policies.txt
│   │   │   └── uid_policies.py
│   │   ├── __init__.py
│   │   ├── anti_tamper_engine.py
│   │   ├── auth_system.py
│   │   ├── contain_engine.py
│   │   ├── decisions_engine.py
│   │   ├── privilege_manager.py
│   │   ├── sensors_manager.py
│   │   └── trip_engine.py
│   ├── sensors
│   │   ├── __init__.py
│   │   ├── dns.py
│   │   ├── filesystem.py
│   │   ├── hardware.py
│   │   ├── human_factors.py
│   │   ├── network.py
│   │   ├── permission.py
│   │   ├── permissions.py
│   │   └── process_lifecycle.py
│   └── __init__.py
├── examples
│   ├── config.sample.yaml
│   └── doctrine.sample.md
├── logs
│   ├── anti_tamper
│   ├── decisions
│   │   └── incidents.log
│   └── sensors
├── scripts
│   ├── __init__.py
│   ├── auth_reset.py
│   ├── check_root.sh
│   ├── check_status.sh
│   ├── clean_temp.sh
│   ├── create_venv.sh
│   ├── daily_report.sh
│   ├── debug_env.sh
│   ├── gen_filetree.py
│   ├── initiate_cockpit.sh
│   ├── inspect_modules.py
│   ├── install_linux.sh
│   ├── install_termux.sh
│   ├── install_windows.ps1
│   ├── reload_config.sh
│   ├── restart.sh
│   ├── root_workaround.sh
│   ├── rotate_logs.sh
│   ├── run_guard.sh
│   ├── schedule_checks.sh
│   ├── set_user_pin.sh
│   ├── setup_env.sh
│   ├── setup_security.py
│   ├── unlock_system.sh
│   ├── update_modules.sh
│   └── update_readme_filetree.py
├── tests
│   └── test_cli.py
├── .gitignore
├── .pre-commit-config.yaml
├── .ruff.toml
├── ARCHITECTURE.md
├── blux_shell.py
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONFIGURATION.md
├── CONTRIBUTING.md
├── initiate_cockpit.py
├── INSTALL.md
├── LICENSE
├── Makefile
├── mypy.ini
├── OPERATIONS.md
├── PRIVACY.md
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
├── ROADMAP.md
├── SECURITY.md
├── SUPPORT.md
└── TROUBLESHOOTING.md
```
</details>
<!-- FILETREE:END -->

