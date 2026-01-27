"""
BLUX Guard Unified Audit Schema
"""

# Record Format

Audit records are JSON objects written as JSONL to `~/.config/blux-guard/logs/audit.jsonl` (or the path defined by `BLUX_GUARD_LOG_DIR`). Fields:

- `ts` (float): Unix timestamp in seconds.
- `level` (str): `debug` | `info` | `warn` | `error`.
- `actor` (str): Source component (`guard`, `telemetry`, `scanner`, etc.).
- `action` (str): Event identifier (e.g., `guard.receipt.issued`).
- `stream` (str): `audit`.
- `payload` (object): Structured data for the action (command text, paths, counts, status).
- `channel` (str): Backward-compatible alias for `action` used by existing telemetry sinks.
- `correlation_id` (str): UUID4 tying related events together.
- `component` (str, optional): Subsystem name (e.g., `receipt`, `telemetry`).

# Guarantees

- **Append-only**: Writes are append-only; no truncation by default.
- **Best-effort**: Logging failures do not crash the operator flow; warnings are emitted to stderr once.

# Paths

- **Audit Log**: `~/.config/blux-guard/logs/audit.jsonl`
- **SQLite Mirror**: `~/.config/blux-guard/logs/telemetry.db` (for fast queries)

# Correlation

- Use `correlation_id` to tie related receipt emissions and constraint checks together.
