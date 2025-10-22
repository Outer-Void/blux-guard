# Changelog

## [Unreleased]
### Added
- `bluxq` CLI dependencies declared (Typer, Textual, etc.).
- Best-effort telemetry (JSONL/SQLite) with env toggles.
- Enterprise doc suite (ARCHITECTURE, INSTALL, OPERATIONS, SECURITY, PRIVACY, CONFIGURATION).
- CI, Dependabot, pre-commit config, base tests.
- Debug/verbose flags for `bluxq` and `bluxqd`, plus a self-check command and sandbox probe.
- README file tree generator with automation scripts (`scripts/gen_filetree.py`, `scripts/update_readme_filetree.py`).

### Fixed
- CLI crash when Typer missing after installation.
- CLI commands now capture exceptions, mirroring tracebacks in debug mode while recording telemetry events.

### Security
- CodeQL scanning workflow introduced.

## [GUARD-PM2-FIX] Add Typer dependency; make telemetry best-effort; docs refresh
- Declare CLI/runtime dependencies including Typer, psutil, FastAPI, and Prometheus exporters.
- Harden telemetry writer with best-effort JSONL/SQLite handling and startup degrade notices.
- Document cockpit usage, CLI commands, telemetry behavior, and troubleshooting across the repo.
