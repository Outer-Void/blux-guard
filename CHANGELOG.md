# Changelog

## [GUARD-PM2-FIX] Add Typer dependency; make telemetry best-effort; docs refresh
- Declare CLI/runtime dependencies including Typer, psutil, FastAPI, and Prometheus exporters.
- Harden telemetry writer with best-effort JSONL/SQLite handling and startup degrade notices.
- Document cockpit usage, CLI commands, telemetry behavior, and troubleshooting across the repo.
