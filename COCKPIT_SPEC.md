"""
BLUX Guard Developer Security Cockpit — Specification
"""

# Overview

The Cockpit provides a unified operator view for BLUX Guard across CLI and TUI surfaces. It focuses on a single operator journey: launch the cockpit (`bluxq guard tui`), observe telemetry, run diagnostics, and export evidence.

# Navigation

- **Home**: Overview banner, current mode (secure/dev/ops), quick links to start scans.
- **Telemetry**: Metrics, process view, YARA scans, credentials audit, and audit chain verification with refresh hotkeys.
- **Rules**: Rule summaries and health indicators.
- **Incidents**: Aggregated audit timeline filtered to warnings/errors plus last export paths.
Each screen emits audit events on entry/exit and on key actions (scan, export).

# Data Contracts

- **Audit Events**: JSONL records defined in `AUDIT_SCHEMA.md`. Each record includes `correlation_id`, `actor`, `action`, `stream`, `payload`, and timestamps.
- **Config Paths**: All writable state lives under `~/.config/blux-guard` by default. Paths can be overridden with environment variables (see `blux_guard/config.py`).
- **Quantum Plugin Surface**: `blux_guard.quantum_plugin.register(app)` expects a Typer app and registers the Guard command tree.

# Flows

1. **Launch**: Operator runs `bluxq guard tui`. CLI creates a correlation_id, records `tui.launch`, and starts the Textual app (`blux_guard.tui.app.CockpitApp`).
2. **Telemetry Refresh**: Hotkeys trigger panel refresh; each refresh logs `tui.refresh` with the screen identifier.
3. **Rules**: Rule view surfaces status summaries and warning hints.
4. **Incidents/Audit**: Timeline reads audit JSONL and shows warnings/errors. Exports write bundles via `security_cockpit.export_diagnostics` and emit `tui.export` events.
5. **Doctor/Verify**: CLI `doctor` and `verify` run environment and config checks, emitting audit events and returning non-zero on failure.

# Compatibility

- `blux_guard/cli/bluxq.py` remains the primary entry point for cockpit and guard operations.
- Existing panels remain intact; new screens orchestrate them for the unified cockpit experience.
