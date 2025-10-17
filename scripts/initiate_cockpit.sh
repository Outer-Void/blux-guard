#!/bin/bash
# BLUX Guard Cockpit Interface Wrapper
# Launches the graphical cockpit interface

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛩️  Launching BLUX Guard Cockpit..."
echo "==================================="

# Check for textual dependency
python3 -c "import textual" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Textual UI not found. Install with: pip install textual"
    exit 1
fi

cd "$BLUX_ROOT"
python3 initiate_cockpit.py "$@"
