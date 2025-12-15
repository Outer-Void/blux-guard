#!/usr/bin/env bash
# BLUX Guard Daily Report
# Summarizes logs and events, sends alert or prints to console
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📈 BLUX Guard Daily Security Report"
echo "===================================="

cd "$BLUX_ROOT"

REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="logs/daily_report_${REPORT_DATE}.txt"

{
    echo "BLUX Guard Daily Security Report"
    echo "Generated: $(date)"
    echo "========================================"
    echo ""
    
    # System overview
    echo "SYSTEM OVERVIEW"
    echo "---------------"
    python3 -c "
import psutil, datetime
boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
uptime = datetime.datetime.now() - boot_time
print(f'System uptime: {uptime}')
print(f'CPU usage: {psutil.cpu_percent()}%')
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
    echo ""
    
    # Security events
    echo "SECURITY EVENTS (Last 24h)"
    echo "-------------------------"
    for log_type in "anti_tamper" "sensors" "decisions"; do
        log_file="logs/${log_type}/$(date +%Y%m%d).log"
        if [ -f "$log_file" ]; then
            count=$(grep -c "ALERT\|WARNING\|ERROR" "$log_file" 2>/dev/null || echo "0")
            echo "$(echo $log_type | tr 'a-z' 'A-Z'): $count events"
        else
            echo "$(echo $log_type | tr 'a-z' 'A-Z'): No log file"
        fi
    done
    echo ""
    
    # Recent alerts
    echo "RECENT ALERTS"
    echo "-------------"
    find logs/ -name "*.log" -type f -mtime -1 -exec grep -h "ALERT\|ERROR" {} \; | tail -5
    
} > "$REPORT_FILE"

echo "✅ Daily report generated: $REPORT_FILE"
cat "$REPORT_FILE"
