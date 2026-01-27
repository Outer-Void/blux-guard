# BLUX Guard

> **Mechanical enforcement layer; emits guard_receipts only.**

[![License](https://img.shields.io/badge/License-Dual-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)

---

## 🎯 Vision

BLUX Guard is a mechanical enforcement layer that emits guard receipts from validated request envelopes and returns deterministic constraints only.

**Explicit non-capabilities:**
- No execution or command running.
- No server/daemon/control-plane services.
- No token issuance, verification, signing, or revocation.
- No policy, ethics, or decision interpretation.
- No orchestration.

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

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SECURITY.md](SECURITY.md) | Threat model, telemetry guarantees |
| [PRIVACY.md](PRIVACY.md) | Telemetry scope and retention controls |
| [CONFIGURATION.md](CONFIGURATION.md) | YAML schema and overrides |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Quick fixes for common issues |
| [docs/ROLE.md](docs/ROLE.md) | Guard enforcement responsibilities and non-goals |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and coding standards |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community expectations |
| [SUPPORT.md](SUPPORT.md) | Escalation paths and SLAs |
| [ROADMAP.md](ROADMAP.md) | Upcoming milestones |

---

## 🔒 Security Model

- Enforcement stays deterministic and receipt-scoped
- All automation routes through receipt constraints to respect containment boundaries

## 🧾 Receipt Enforcement (No Elevation)

BLUX Guard issues receipts that describe allowed commands or paths, plus explicit sandbox
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

BLUX Guard targets Python 3.9+ for runtime compatibility.

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
- See [SUPPORT.md](SUPPORT.md) for escalation paths

---

## 📞 Contact

- **Email:** outervoid.blux@gmail.com
- **GitHub:** [github.com/Outer-Void](https://github.com/Outer-Void)
