# Installation Guide

BLUX Guard supports Android/Termux, Linux (including WSL2), macOS, and Windows. All instructions preserve
existing cockpit entry points while enabling the new `bluxq` CLI.

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
bluxq guard self-check
```

Pass `--debug` or `--verbose` to any `bluxq` command when additional telemetry mirrors are required.

## Android / Termux

1. Install dependencies: `pkg install python git clang make`.
2. Clone the repository and run `scripts/install_termux.sh` to register the `bluxq` alias.
3. Telemetry writes to `$HOME/.config/blux-guard/logs`; run `termux-setup-storage` if you see permission prompts.
4. Start the cockpit with `bluxq guard tui --mode dev` inside Termux or termux-x11.

## Linux / WSL2

1. Ensure Python 3.9+ is installed (`sudo apt install python3 python3-venv`).
2. Execute `scripts/install_linux.sh` to create the shell alias and install requirements.
3. Launch the daemon (`bluxqd &`) and then run `bluxq guard tui --mode secure` for production monitoring.

## macOS

1. Install Homebrew Python 3.11+ or use the system Python if it meets the minimum version.
2. Run `pip install -e .` from inside a virtual environment (recommended via `python -m venv .venv`).
3. The cockpit shell panel defaults to `/bin/zsh`; adjust via configuration overrides in `config/local.yaml`.

## Windows

1. Use PowerShell 7+ and install Python 3.11 from the Microsoft Store or python.org.
2. Run `scripts\install_windows.ps1` from an elevated PowerShell prompt to create the `bluxq` function.
3. Telemetry logs live in `%USERPROFILE%\.config\blux-guard\logs`.
4. Start the daemon in one window (`bluxqd`) and launch the cockpit from another (`bluxq guard tui --mode dev`).

## Verification

- `bluxq --help` shows available subcommands.
- The telemetry directory exists even when unwritable (best-effort logging ensures the app continues running).
- `bluxqd` surfaces a degrade warning instead of crashing when logs are unavailable.
