#!/usr/bin/env bash
# BLUX Guard Config Reload
# Forces reload of /rules/rules.json and sensor configs
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 BLUX Guard Configuration Reload"
echo "==================================="

cd "$BLUX_ROOT"

# Send reload signal to running processes
if [ -f ".blux_pid" ]; then
    PID=$(cat ".blux_pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Sending reload signal to BLUX Guard (PID: $PID)..."
        kill -USR1 "$PID"
        echo "✅ Reload signal sent"
    else
        echo "⚠️  BLUX Guard not running (stale PID file)"
        rm -f ".blux_pid"
    fi
else
    echo "ℹ️  No running BLUX Guard process found"
fi

# Validate configuration files
echo "Validating configuration..."
python3 -c "
import json
from pathlib import Path

configs = {
    'rules': 'rules/rules.json',
    'auth': 'config/auth.json'
}

for name, path in configs.items():
    try:
        with open(path) as f:
            data = json.load(f)
        print(f'✅ {name}: Valid JSON, {len(data)} sections')
    except Exception as e:
        print(f'❌ {name}: {e}')
"

# Clear any cached configs
echo "Clearing cache..."
find . -name "*cache*" -type f -delete 2>/dev/null || true

echo "✅ Configuration reload complete"
echo "💡 Changes will take effect on next operation"
