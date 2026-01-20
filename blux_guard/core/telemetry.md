# Telemetry & Auditing Guide

The telemetry module records guard activity to JSONL and SQLite sinks without introducing runtime failures.

## File Locations

- `~/.config/blux-guard/logs/audit.jsonl` – general guard activity
- `~/.config/blux-guard/logs/telemetry.db` – optional SQLite mirror (`events` table)

Override the base directory with `BLUX_GUARD_LOG_DIR`.

## Failure Handling

All writes are best-effort:

- JSONL/SQLite errors emit a single warning to stderr when `BLUX_GUARD_TELEMETRY_WARN=once`.
- Failures never raise exceptions to callers.
- Set `BLUX_GUARD_TELEMETRY=off` to disable persistence entirely.

## Rotation & Hygiene

- Use the SQLite database to batch-export events when required (`sqlite-utils rows telemetry.db events`).
- Rotate JSONL files with your preferred log rotation tooling or custom cron jobs.
- Delete or archive the JSONL/SQLite files safely; new files will be created automatically on the next write attempt.

## Privacy

Only local actions are recorded. Actors are tagged (`cli`, `daemon`, etc.) for traceability without transmitting data off-device.
