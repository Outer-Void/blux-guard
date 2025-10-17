#!/bin/bash
# BLUX Guard Root Check
# Detects if running as root and adjusts execution flow

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "👑 BLUX Guard Privilege Check"
echo "=============================="

is_root() {
    if [ "$(id -u)" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

if is_root; then
    echo "✅ Running as root - full system access available"
    echo "⚠️  Warning: Running as root increases security responsibility"
    
    # Export root flag for other scripts
    export BLUX_ROOT_MODE=1
    
    # Check if we should drop privileges
    if [ "$1" = "--drop" ]; then
        echo "Dropping to non-root user execution..."
        exec sudo -u "$SUDO_USER" "$0" "${@:2}"
    fi
else
    echo "ℹ️  Running as user $USER - limited system access"
    echo "💡 Some features may require root. Use sudo if needed."
    export BLUX_ROOT_MODE=0
fi

# Pass through to next command if provided
if [ $# -gt 0 ] && [ "$1" != "--drop" ]; then
    exec "$@"
fi
