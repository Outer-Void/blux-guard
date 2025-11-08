#!/usr/bin/env bash
# Idempotent Termux installer for bluxq CLI.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python -m pip install --upgrade pip
pip install .
echo "alias bluxq='python -m blux_guard.cli.bluxq'" >> "$HOME/.bashrc"
echo "BLUX Guard Termux installer completed."
