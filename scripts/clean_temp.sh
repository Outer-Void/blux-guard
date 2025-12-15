#!/usr/bin/env bash
# BLUX Guard Temp Cleaner
# Removes temp files, old cache, .pyc files
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧹 BLUX Guard Temp Cleanup"
echo "==========================="

cd "$BLUX_ROOT"

# Remove Python cache files
echo "Cleaning Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null

# Remove temporary files
echo "Cleaning temporary files..."
find . -name "*.tmp" -delete
find . -name "*.temp" -delete
find . -name ".~lock.*" -delete

# Clean backup directories older than 30 days
echo "Cleaning old backups..."
if [ -d "./backups" ]; then
    find "./backups" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null
fi

# Clear system temp if accessible
if [ -d "/tmp" ]; then
    find "/tmp" -name "blux_*" -mtime +1 -delete 2>/dev/null || true
fi

echo "✅ Cleanup complete"
