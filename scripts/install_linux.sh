#!/usr/bin/env bash
# Idempotent Linux installer for bluxq CLI.
set -euo pipefail
python -m pip install --upgrade pip
pip install .
if ! command -v bluxq >/dev/null 2>&1; then
  cat <<'ALIASEOF' >> "$HOME/.bashrc"
# BLUX Guard Developer Suite
alias bluxq='python -m blux_guard.cli.bluxq'
ALIASEOF
fi
echo "BLUX Guard Linux installer completed."
