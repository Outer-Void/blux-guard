# Contributing Guide

We welcome patches that respect the BLUX Guard non-destructive covenant.

## Development Environment

1. Fork and clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # PowerShell: .venv\\Scripts\\Activate.ps1
   pip install -U pip
   pip install -e .[dev]
   ```
3. Install pre-commit hooks: `pre-commit install`.

## Coding Standards

- Follow Ruff and MyPy guidance (`make lint`).
- New modules should integrate with `telemetry.record_event` instead of writing directly to files.
- Maintain compatibility with Termux, Linux, macOS, and Windows.

## Testing

Run `make test` locally. CI executes Ruff, MyPy (non-fatal), and Pytest across Python 3.9–3.11.

## Documentation

Update relevant docs when adding features. The README links to the documentation suite; keep entries current.
Use `make filetree` after adding or renaming files to refresh the collapsible repository tree in the README.

## Pull Requests

- Reference the appropriate `[ENTERPRISE]` or `[GUARD-*]` tag in commit subjects when applicable.
- Include a summary of tests executed.
- Ensure non-destructive changes: do not remove or overwrite existing legacy modules.

## Code of Conduct

Participation is governed by `CODE_OF_CONDUCT.md`.
