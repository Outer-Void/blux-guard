#!/bin/bash
# BLUX Guard System Status Check
# Shows health of all modules (security engines, sensors, logs, etc)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📊 BLUX Guard System Status"
echo "============================"

# Source environment
if [ -f "$SCRIPT_DIR/.blux_env" ]; then
    source "$SCRIPT_DIR/.blux_env"
fi

cd "$BLUX_ROOT"

# Check Python modules
echo "1. Checking Python modules..."
python3 -c "
try:
    from blux_modules.security_engine import SecurityEngine
    from blux_modules.sensor_manager import SensorManager
    from blux_modules.decision_engine import DecisionEngine
    from blux_modules.anti_tamper import AntiTamper
    print('✅ Core modules: OK')
except ImportError as e:
    print('❌ Core modules:', e)
"

# Check log directories
echo "2. Checking log directories..."
for log_dir in "logs/anti_tamper" "logs/sensors" "logs/decisions"; do
    if [ -d "$log_dir" ] && [ -w "$log_dir" ]; then
        count=$(find "$log_dir" -name "*.log" 2>/dev/null | wc -l)
        echo "   ✅ $log_dir: $count log files, writable"
    else
        echo "   ❌ $log_dir: Missing or not writable"
    fi
done

# Check config files
echo "3. Checking configuration..."
for config in "rules/rules.json" "config/auth.json"; do
    if [ -f "$config" ]; then
        size=$(stat -f%z "$config" 2>/dev/null || stat -c%s "$config" 2>/dev/null)
        echo "   ✅ $config: ${size} bytes"
    else
        echo "   ⚠️  $config: Missing (run setup_security.py)"
    fi
done

# Check system resources
echo "4. System resources..."
python3 -c "
import psutil, os
pid = os.getpid()
process = psutil.Process(pid)
memory_mb = process.memory_info().rss / 1024 / 1024
print(f'   Memory: {memory_mb:.1f} MB')
print(f'   CPU: {psutil.cpu_percent(interval=1)}%')
"

echo "✅ Status check complete"
