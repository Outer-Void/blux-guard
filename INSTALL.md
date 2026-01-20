# Installation Guide

BLUX Guard supports Android/Termux, Linux (including WSL2), macOS, and Windows. All instructions preserve
existing cockpit entry points while enabling the new `bluxq` CLI.

BLUX Guard is protocol enforcement + userland constraints.

## Common Steps

```bash
python -m pip install -U pip
pip install -e .[dev]  # falls back to -e . if optional deps unavailable
```

After installation, launch the daemon and cockpit:

```bash
bluxqd &
bluxq guard status
bluxq guard tui --mode dev
```

## Android / Termux

1. Install dependencies: `pkg install python git clang make`.
2. Clone the repository and install the package with `pip install -e .`.
3. Telemetry writes to `$HOME/.config/blux-guard/logs`; run `termux-setup-storage` if you see permission prompts.
4. Start the cockpit with `bluxq guard tui --mode dev` inside Termux or termux-x11.

## Linux / WSL2

1. Ensure Python 3.9+ is installed via your system package manager (for example, install
   `python3` and `python3-venv` on Debian/Ubuntu).
2. Install the package with `pip install -e .` (optionally inside a virtual environment).
3. Launch the daemon (`bluxqd &`) and then run `bluxq guard tui --mode secure` for production monitoring.

## macOS

1. Install Homebrew Python 3.11+ or use the system Python if it meets the minimum version.
2. Run `pip install -e .` from inside a virtual environment (recommended via `python -m venv .venv`).
3. Adjust configuration overrides in `config/local.yaml` as needed.

## Windows

1. Use PowerShell 7+ and install Python 3.11 from the Microsoft Store or python.org.
2. Install the package with `pip install -e .` and ensure your Python scripts directory is on `PATH`.
3. Telemetry logs live in `%USERPROFILE%\.config\blux-guard\logs`.
4. Start the daemon in one window (`bluxqd`) and launch the cockpit from another (`bluxq guard tui --mode dev`).

## Verification

- `bluxq --help` shows available subcommands.
- The telemetry directory exists even when unwritable (best-effort logging ensures the app continues running).
- `bluxqd` surfaces a degrade warning instead of crashing when logs are unavailable.
