# BLUX Guard Architecture

## High-Level Overview

BLUX Guard combines legacy protection engines with the new Developer Suite cockpit. The system keeps the
original security pipeline while routing modern workflows through the developer-oriented
runtime:

1. **Interface Layer** — `blux_guard/cli/bluxq.py` Quantum CLI and Textual TUI components under
   `blux_guard/tui/`.
2. **Execution Layer** — receipt issuance from `blux_guard/core/receipt.py` and development flows in
   `blux_guard/core/devsuite.py`.
3. **Telemetry Layer** — `blux_guard/core/telemetry.py` streams JSONL and SQLite mirrors while the API
   exposes Prometheus metrics.
4. **Platform Agents** — `blux_guard/agents/` collects host data per OS and reports to the daemon.
5. **Daemon & API** — `blux_guard/api/guardd.py` launches the FastAPI server in `blux_guard/api/server.py`
   and relays cockpit events through `blux_guard/api/stream.py`.

## Control Flow

```
bluxq → runtime.ensure_supported_python → receipt.issue_guard_receipt → telemetry.record_event
```

1. Commands enter through the CLI or cockpit.
2. Receipt issuance is deterministic and protocol-scoped.
3. Results, audits, and metrics emit through `telemetry.record_event` which never raises on I/O errors.
4. The daemon and TUI subscribe to telemetry streams and update panels in real time.

## Module Relationships

- `blux_guard/core/__init__.py` exposes the developer runtime modules.
- Legacy sensors and trip engines are handled through the guard receipt engine.
- Agents call back into `telemetry` so all platforms share a unified audit surface.

## Platform Matrix

| Component            | Android / Termux | Linux / WSL2 | macOS | Windows |
|----------------------|------------------|--------------|-------|---------|
| CLI (`bluxq`)        | ✅ Termux        | ✅ Native    | ✅    | ✅ PowerShell |
| TUI (`dashboard`)    | ✅ (termux-x11)  | ✅ Native    | ✅    | ✅ Windows Terminal |
| Daemon (`bluxqd`)    | ✅ uvicorn       | ✅ uvicorn   | ✅    | ✅ (uvicorn + asyncio) |
| Agents               | Termux agent     | Linux agent  | mac agent | Windows agent |
| Telemetry storage    | `$HOME/.config`  | `$HOME/.config` | `$HOME/Library/Application Support` equivalent | `%USERPROFILE%\.config` |

## Future Extensions

- Commander web cockpit mirrors via `/api/stream`.
- SBOM generation and SLSA compliance in CI.
- Extended receipt policies for containerized builds.
