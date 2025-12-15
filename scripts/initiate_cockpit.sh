#!/usr/bin/env bash
# BLUX Guard Cockpit Interface Wrapper
# Launches the graphical cockpit interface
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛩️  Launching BLUX Guard Cockpit..."
echo "==================================="

# Check for textual dependency
if ! python3 -c "import textual" 2>/dev/null; then
    echo "❌ Textual UI not found. Install with: pip install textual"
    exit 1
fi

cd "$BLUX_ROOT"
python3 initiate_cockpit.py "$@"
