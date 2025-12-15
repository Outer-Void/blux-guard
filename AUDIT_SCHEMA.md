"""
BLUX Guard Unified Audit Schema
"""

# Record Format

Audit records are JSON objects written as JSONL to `~/.config/blux-guard/logs/audit.jsonl` (or the path defined by `BLUX_GUARD_LOG_DIR`). Fields:

- `ts` (float): Unix timestamp in seconds.
- `level` (str): `debug` | `info` | `warn` | `error`.
- `actor` (str): Source component (`cli`, `tui`, `devshell`, `scanner`, etc.).
- `action` (str): Event identifier (e.g., `tui.launch`, `cli.doctor`, `devshell.exec`).
- `stream` (str): `audit` or `devshell`.
- `payload` (object): Structured data for the action (command text, paths, counts, status).
- `channel` (str): Backward-compatible alias for `action` used by existing telemetry sinks.
- `correlation_id` (str): UUID4 tying related events together.
- `component` (str, optional): Subsystem name (e.g., `quantum_plugin`, `install`).

# Guarantees

- **Append-only**: Writes are append-only; no truncation by default.
- **Best-effort**: Logging failures do not crash the operator flow; warnings are emitted to stderr once.
- **Safe-mode**: When doctrine or registry keys are unavailable, actions record `safe_mode=true` in payload and avoid containment steps.

# Paths

- **Audit Log**: `~/.config/blux-guard/logs/audit.jsonl`
- **DevShell Log**: `~/.config/blux-guard/logs/devshell.jsonl`
- **SQLite Mirror**: `~/.config/blux-guard/logs/telemetry.db` (for fast queries)

# Correlation

- CLI commands create a `correlation_id` at invocation and pass it into TUI, exports, and devshell sessions.
- TUI screen transitions emit `tui.screen.enter`/`exit` events with the same correlation id when available.
- DevShell commands include both `session_id` and `correlation_id` fields in their payloads.
