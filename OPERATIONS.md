# Operations Runbook

## Starting and Stopping Services

- **Start daemon**: `bluxqd` (runs FastAPI server and agent pollers).
- **Stop daemon**: Ctrl+C from the daemon terminal or send SIGTERM to the process.
- **Launch cockpit**: `bluxq guard tui --mode dev` for development, `--mode secure` for monitoring.

## Log Rotation

Logs are appended to `~/.config/blux-guard/logs`. Rotate by moving files and recreating empty placeholders:

```bash
mkdir -p ~/.config/blux-guard/archive
mv ~/.config/blux-guard/logs/*.jsonl ~/.config/blux-guard/archive/
```

SQLite mirrors can be vacuumed:

```bash
sqlite3 ~/.config/blux-guard/logs/telemetry.db 'VACUUM;'
```

## Environment Toggles

- `BLUX_GUARD_TELEMETRY=off` — disable JSONL/SQLite writes.
- `BLUX_GUARD_TELEMETRY_WARN=once` — print a single degrade warning to stderr on failure.
- `BLUX_GUARD_LOG_DIR=/custom/path` — override the log directory.

## Backup & Restore

1. Copy configuration files under `config/` and any `config/local.yaml` overrides.
2. Archive telemetry logs if needed for audit trails.
3. Restore by placing files back into the repository checkout and re-running `pip install -e .` if dependencies
   changed.

## Health Checks

- `bluxq guard status` — ensures telemetry paths resolve correctly.
- `curl http://localhost:8000/status` — verify daemon API is running.
- `curl http://localhost:8000/metrics` — fetch Prometheus metrics for monitoring.

## Incident Response

1. Review `audit.jsonl` for recent events.
2. Check Doctrine panel in the TUI for alignment violations.
3. Use `bluxq dev deploy --safe` to redeploy with rollback protection if necessary.
4. Document the response in your operational tracker.
