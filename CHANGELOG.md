# Changelog

## [Unreleased]
### Added
- `bluxq` CLI dependencies declared (Typer, Textual, etc.).
- Best-effort telemetry (JSONL/SQLite) with env toggles.
- Enterprise doc suite (ARCHITECTURE, INSTALL, OPERATIONS, SECURITY, PRIVACY, CONFIGURATION).
- CI, Dependabot, pre-commit config, base tests.

### Fixed
- CLI crash when Typer missing after installation.

### Security
- CodeQL scanning workflow introduced.

## [GUARD-PM2-FIX] Add Typer dependency; make telemetry best-effort; docs refresh
- Declare CLI/runtime dependencies including Typer, psutil, FastAPI, and Prometheus exporters.
- Harden telemetry writer with best-effort JSONL/SQLite handling and startup degrade notices.
- Document cockpit usage, CLI commands, telemetry behavior, and troubleshooting across the repo.
