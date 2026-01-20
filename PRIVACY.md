# Privacy and Telemetry

BLUX Guard stores telemetry locally on the operator's device. No automatic uploads occur.

## Data Collected

- Event metadata: timestamps, action names, actor identifiers, severity levels.
- Optional payloads describing resource usage or receipt metadata (sanitized).

## Storage Locations

- JSONL audit log: `~/.config/blux-guard/logs/audit.jsonl`
- SQLite mirror: `~/.config/blux-guard/logs/telemetry.db`

## Controls

- Disable telemetry: set `BLUX_GUARD_TELEMETRY=off` before launching `bluxq` or `bluxqd`.
- Limit warnings: `BLUX_GUARD_TELEMETRY_WARN=once` prints a single degrade message when storage fails.
- Custom location: `BLUX_GUARD_LOG_DIR=/custom/path` redirects all files.

## Retention & Rotation

Operators manage retention manually. Use the guidance in `OPERATIONS.md` to rotate logs or purge data as
required by policy.

## Access

Telemetry files are created with user-level permissions. Share them only with trusted auditors. No upstream
services receive telemetry unless you integrate optional exporters.
