# Security Posture

## Threat Model

- **Adversaries**: Malware attempting to tamper with guard modules, unauthorized operators, and remote
  attackers seeking unauthorized access.
- **Assets**: Device integrity, receipt integrity, audit trails, and developer workflows.

## Key Controls

1. **Receipt Issuance** — `core/receipt.py` emits deterministic receipts with explicit constraints.
2. **Telemetry Assurance** — `core/telemetry.py` logs events without risking crashes; degrade warnings are
   emitted once when `BLUX_GUARD_TELEMETRY_WARN=once`.
3. **Role Separation** — CLI commands map to user roles; dangerous operations require explicit
   confirmation via `--safe` flags.

## Disclosure & Updates

- Report vulnerabilities through the support channel listed in `SUPPORT.md`.
- Security fixes are documented in `CHANGELOG.md` under the **Security** heading.

## Telemetry & Failure Behavior

All telemetry writes are wrapped in best-effort handlers. If paths are unwritable or SQLite is locked, the
application continues and emits a single degrade warning when `BLUX_GUARD_TELEMETRY_WARN=once`.

## Hardening Tips

- Keep Python and system dependencies updated via Dependabot recommendations.
- Run CI workflows (`.github/workflows/ci.yml`) on every branch.
- Rotate any operator credentials stored outside the repository (e.g., Termux tokens) regularly.
