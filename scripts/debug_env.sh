#!/usr/bin/env bash
# BLUX Guard Debug Environment
# Launches a testing TUI or logging sandbox
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🐛 BLUX Guard Debug Environment"
echo "==============================="

cd "$BLUX_ROOT"

# Source environment
if [ -f "$SCRIPT_DIR/.blux_env" ]; then
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/.blux_env"
fi

# Check for debug mode
export BLUX_DEBUG=1
export PYTHONPATH="$BLUX_ROOT:${PYTHONPATH:-}"

# Launch appropriate debug interface
case "${1:-}" in
    "tui")
        echo "Launching Textual Debug Interface..."
        python3 -c "
from blux_cli.debug_console import DebugConsole
DebugConsole().run()
"
        ;;
    "sandbox")
        echo "Launching Logging Sandbox..."
        python3 -c "
import logging
from blux_modules.security_engine import SecurityEngine
from blux_modules.sensor_manager import SensorManager

# Set verbose logging
logging.basicConfig(level=logging.DEBUG)

print('🧪 Security Engine Test')
engine = SecurityEngine()
engine.self_test()

print('\\n🧪 Sensor Manager Test')
sensors = SensorManager()
sensors.self_test()
"
        ;;
    *)
        echo "Available debug modes:"
        echo "  tui     - Textual debug console"
        echo "  sandbox - Logging and module testing sandbox"
        echo ""
        echo "Usage: $0 [tui|sandbox]"
        ;;
esac
