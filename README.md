# BLUX Guard

> **Developer Security Cockpit for the BLUX Ecosystem**  
> Real-time defense, telemetry, and doctrine-aware sandboxing integrated with AI orchestration.

[![License](https://img.shields.io/badge/License-Dual-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Android-lightgrey.svg)](#cross-platform-support)

---

## 🎯 Vision

BLUX Guard is a discreet, layered security defender that uses deterministic trip-variables, tamper-resistant sensors, and safe containment to protect **your own devices**. It operates transparently, remains fully auditable, and stays under operator control at all times.

BLUX Guard provides protocol enforcement + userland constraints, and **no root required** for setup or operation.
Enforcement stays safely in userland by applying receipt-defined constraints to Guard actions
and relying on non-privileged checks (filesystem scoping, process boundaries, and explicit
operator confirmations) instead of any elevated system controls.

**Core Principles:**
- 🔒 Defensive-only security with no offensive payloads
- 🔍 Transparent operation with complete auditability
- 🛡️ Multi-layered protection against AI-powered threats
- 👤 Always respects operator authority and privacy

---

## 🏗️ Architecture Overview

```
Sensors → Trip Engine → Decision Layer → Containment → Operator
```

### 1. **Sensors** (Data Sources)
- Network flows, DNS queries, process lifecycle monitoring
- Filesystem changes and permission modifications
- Hardware events: charging, Bluetooth pairing, USB attach
- Human factors: unlock patterns, presence windows

### 2. **Trip Engine** (Deterministic Rules)
- Boolean and temporal trip-wires
- Thresholded counters and state chains
- Signed, versioned rule manifests in `.config/rules/rules.json`

### 3. **Decision Layer**
- Escalation path: observe → intercept → quarantine → lockdown
- Per-UID policies: whitelist / greylist / blacklist
- Optional kill-switch for complete isolation

### 4. **Containment & Response**
- Network interceptor (VpnService-like)
- Process isolator with snapshot & rollback
- Filesystem quarantine and permission reverter
- Signed incident logs in `logs/decisions/incidents.log`

### 5. **Integrity & Anti-Tamper**
- Watchdog with self-heartbeat monitoring
- Signed binaries and manifests
- Alerts on package manager changes, privilege escalation binaries, SELinux modifications

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Outer-Void/blux-guard.git
cd blux-guard

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### CLI Usage

```bash
# Start with the CLI
bluxq guard status

# Evaluate a request envelope and emit a receipt
blux-guard evaluate --request-envelope examples/envelope.json --token TOKEN_VALUE
```

### Power Mode 2.0 (Recommended)

```bash
# Install with virtual environment (recommended)
python -m pip install -U pip
pip install -e .

# Start daemon & open cockpit
bluxqd &
bluxq guard status
bluxq guard tui --mode dev
```

### Developer Workflows

```bash
bluxq dev init        # Initialize development environment
bluxq dev shell       # Open developer shell
bluxq dev scan .      # Scan current directory
bluxq dev deploy --safe  # Deploy with safety checks
```

## 🎯 Trip Engine Examples

BLUX Guard uses deterministic, time-bounded, and auditable trip conditions:

| Scenario | Trip Condition | Action |
|----------|---------------|--------|
| **Silent Exfil** | 10 external sockets to distinct IPs in 60s | Block, snapshot, notify |
| **Mount Surprise** | SD mounted while locked & charging & idle 12h+ | Read-only + checksum |
| **Privilege Creep** | New permission soon after unknown net conn | Revert + quarantine |
| **Process Mimic** | Same pkg name, different cert/hash | Freeze + capture |
| **UI Hijack** | Overlay within 2s of credential event | Block overlay + prompt |
| **Cold-start Lateral** | Unknown AUTOSTART after reboot | Block autostart until review |

---

## 🤖 AI Security Strategy

**Principle:** Break hostile AI effectiveness by destroying input reliability and computation economics.

### Strategy I — "Pull It Apart"
- Deterministic jitter to break time-series features
- Proof-of-Work throttles (per-UID PoW)
- Honeypots and deceptive metadata
- Never auto-confirm success — require human validation

### Strategy II — "EMP Metaphor"
- Circuit breakers to air-gap radios or network routes
- Freeze/snapshot suspect processes
- Reduce CPU/QoS for suspect UIDs
- All actions signed and operator-approved

---

## 📊 Telemetry & Reliability

BLUX Guard writes best-effort logs to:

- `~/.config/blux-guard/logs/audit.jsonl`
- `~/.config/blux-guard/logs/devshell.jsonl` (developer shell stream)
- `~/.config/blux-guard/logs/telemetry.db` (SQLite, optional)

If the directory is unwritable or SQLite is unavailable, logging **degrades silently** and the app **continues running**.

### Telemetry Controls

```bash
# Disable telemetry writes
export BLUX_GUARD_TELEMETRY=off

# Show single degrade warning on stderr
export BLUX_GUARD_TELEMETRY_WARN=once
```

---

## 🌍 Cross-Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Android / Termux** | ✅ Full Support | Installers configure aliases; telemetry lives under `$HOME/.config/blux-guard/logs` |
| **Linux** | ✅ Full Support | Sandbox shell defaults to `/bin/bash`, Prometheus metrics export via `bluxqd` |
| **macOS** | ✅ Full Support | Shell panel launches `/bin/zsh` while retaining doctrine validation |
| **Windows** | ✅ Full Support | PowerShell support via `COMSPEC`; telemetry paths expand to `%USERPROFILE%\.config\blux-guard\logs` |
| **WSL2** | ✅ Full Support | Works like native Linux installation |

---

## 🐛 Troubleshooting

### Common Issues

**CLI reports `ModuleNotFoundError: typer`**
```bash
# Reinstall with dependencies
pip install -e .
```

**Permission denied writing logs**
```bash
# Create the telemetry directory manually
mkdir -p ~/.config/blux-guard/logs

# Or disable telemetry
export BLUX_GUARD_TELEMETRY=off
```

**SQLite locked or missing**
- Mirror is optional; CLI continues using JSONL streams
- Emits a single degrade warning when enabled

**Termux storage prompts**
```bash
# Grant write access
termux-setup-storage
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Module graph and platform matrix |
| [INSTALL.md](INSTALL.md) | Platform-specific installation steps |
| [OPERATIONS.md](OPERATIONS.md) | Runbook for day-two operations |
| [SECURITY.md](SECURITY.md) | Threat model, doctrine enforcement, telemetry guarantees |
| [PRIVACY.md](PRIVACY.md) | Telemetry scope and retention controls |
| [CONFIGURATION.md](CONFIGURATION.md) | YAML schema and overrides |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Quick fixes for common issues |
| [docs/ROLE.md](docs/ROLE.md) | Guard enforcement responsibilities and non-goals |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and coding standards |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community expectations |
| [SUPPORT.md](SUPPORT.md) | Escalation paths and SLAs |
| [ROADMAP.md](ROADMAP.md) | Upcoming milestones |

---

## 🗺️ Roadmap

| Stage | Goal |
|-------|------|
| v0.1 | Termux Trip Engine prototype |
| v0.2 | Honeypot + canary endpoint |
| v0.3 | BLE companion listener |
| v0.4 | Kotlin VpnService interceptor |
| v0.5 | Consensus agent coordinator |
| v1.0 | Full BLUX Guard operator suite |

---

## 🔒 Security Model & Doctrine Alignment

- **User / Operator / Elevated (cA)** tiers remain enforced
- Developer flows inherit doctrine checks before privileged actions
- All automation routes through sandboxed PTY shell to respect containment boundaries
- Doctrine integrations surface alignment scores directly inside the cockpit and via CLI

## 🧾 Receipt Enforcement (No Elevation)

BLUX Guard issues signed receipts that describe allowed commands or paths, plus explicit sandbox
and network constraints. Enforcement is intentionally non-privileged: receipts describe what an
agent may do, and downstream runners can enforce those rules without requiring any elevation.
If you need broader access, adjust the request envelope constraints instead of escalating.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:

- Contribution workflow
- Coding standards
- Testing requirements
- Review process

All commits and rule changes must include:
- Author signature
- Simulation or test logs
- One reviewer sign-off

---

## 🔐 Governance & Ethics

**Defensive-only.** No offensive payloads.

### Security Protocols

- Private signing keys must never reside on the same device
- Critical changes require physical ACK (BLE/NFC or manual gesture)
- Maintain an auditable signed changelog

---

## ⚖️ Licensing

BLUX Guard is dual-licensed:

- **Open-source use:** [Apache License 2.0](LICENSE-APACHE)
- **Commercial use:** Requires separate agreement (see [LICENSE-COMMERCIAL](LICENSE-COMMERCIAL))

### Apache 2.0 Usage
You may use, modify, and redistribute the software for open and internal purposes, provided that you preserve notices, include the license, and accept the standard disclaimers of warranty and liability.

### Commercial Usage
Commercial use—such as embedding in paid products, offering hosted services, or other monetized deployments—requires a commercial license. Please review [COMMERCIAL.md](COMMERCIAL.md) for examples and contact **theoutervoid@outlook.com** to arrange commercial terms.

---

## 📋 Supported Python Versions

The cockpit validates Python 3.9+ on startup. 

**Supported interpreters:** 3.9, 3.10, 3.11

Upgrade the interpreter if you receive a startup warning.

---

## 🛡️ Legal & Safety

- ✅ Works only on devices you own or control
- ✅ Forensics data remains private and encrypted
- ✅ Always test on secondary hardware first
- ✅ Never modify or erase evidence automatically

---

## 💬 Getting Help

- Check individual module docstrings for usage details
- Use the CLI for guided operation
- See [SUPPORT.md](SUPPORT.md) for escalation paths

---

## 📞 Contact

- **Email:** outervoid.blux@gmail.com
- **GitHub:** [github.com/Outer-Void](https://github.com/Outer-Void)

---

**BLUX Guard Doctrine** — Building walls that respect your hunger and deny the pack.

*"The forge remains open, even when the pen runs dry."*
