#!/usr/bin/env bash
# show_motd.sh — Cross-platform MOTD for Blux Guard Ultra
# Compatible with: WSL2, Linux, Windows (Git Bash), macOS, Android Termux

set -euo pipefail

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Linux)
            if grep -q -i "microsoft" /proc/version 2>/dev/null || [[ -d "/run/WSL" ]]; then
                echo "wsl2"
            elif [[ -d "/system/app" ]] || [[ -d "/system/priv-app" ]] || [[ "$(uname -o)" == "Android" ]]; then
                echo "android"
            else
                echo "linux"
            fi
            ;;
        Darwin) echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

PLATFORM=$(detect_platform)

# Configuration paths with platform-specific defaults
setup_paths() {
    local config_dir=""
    
    case "$PLATFORM" in
        wsl2|linux)
            config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/blux-guard"
            ;;
        macos)
            config_dir="$HOME/Library/Application Support/Blux Guard"
            ;;
        windows)
            if [[ -n "${APPDATA:-}" ]]; then
                config_dir="$APPDATA/Blux Guard"
            else
                config_dir="$HOME/.blux-guard"
            fi
            ;;
        android|termux)
            config_dir="$HOME/.config/blux-guard"
            ;;
        *)
            config_dir="$HOME/.blux-guard"
            ;;
    esac
    
    # Create directory if it doesn't exist
    if [[ ! -d "$config_dir" ]]; then
        mkdir -p "$config_dir" 2>/dev/null || {
            echo "Warning: Cannot create config directory: $config_dir" >&2
            # Fallback to home directory
            config_dir="$HOME/.blux-guard"
            mkdir -p "$config_dir" 2>/dev/null || true
        }
    fi
    
    HEADER="$config_dir/motd_header.txt"
    DYN_SCRIPT="$config_dir/motd_dynamic.py"
    
    export HEADER DYN_SCRIPT
}

# Create default header if missing
create_default_header() {
    if [[ ! -f "$HEADER" ]]; then
        cat > "$HEADER" << 'EOF'
┌──────────────────────────────────────────────────────────────────────────────┐
│                        🛡️  BLUX GUARD ULTRA  🛡️                         │
├──────────────────────────────────────────────────────────────────────────────┤
│     ACTIVE     │     COCKPIT     │    SECURE    │    READY    │   ONLINE     │
└──────────────────────────────────────────────────────────────────────────────┘
EOF
        echo "Created default header at: $HEADER" >&2
    fi
}

# Check Python and dependencies
check_python_deps() {
    if ! command -v python3 >/dev/null 2>&1; then
        return 1
    fi
    
    # Test if Python can import required modules
    if ! python3 -c "import psutil, platform, shutil, socket, datetime" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

# Install missing Python dependencies
install_python_deps() {
    local pip_cmd="pip3"
    
    if command -v pip3 >/dev/null 2>&1; then
        echo "Installing required Python packages..." >&2
        if pip3 install psutil 2>/dev/null; then
            return 0
        fi
    fi
    
    # Platform-specific installation methods
    case "$PLATFORM" in
        linux|wsl2)
            if command -v apt >/dev/null 2>&1; then
                sudo apt update && sudo apt install -y python3-psutil 2>/dev/null && return 0
            elif command -v yum >/dev/null 2>&1; then
                sudo yum install -y python3-psutil 2>/dev/null && return 0
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -S --noconfirm python-psutil 2>/dev/null && return 0
            fi
            ;;
        macos)
            if command -v brew >/dev/null 2>&1; then
                brew install psutil 2>/dev/null && return 0
            fi
            ;;
        android|termux)
            if command -v pkg >/dev/null 2>&1; then
                pkg install -y python psutil 2>/dev/null && return 0
            fi
            ;;
    esac
    
    return 1
}

# Create dynamic script if missing
create_dynamic_script() {
    if [[ ! -f "$DYN_SCRIPT" ]]; then
        cat > "$DYN_SCRIPT" << 'PYTHON_EOF'
#!/usr/bin/env python3
# motd_dynamic.py — Cross-platform system status monitor

import sys
import os

try:
    import psutil
    import platform
    import shutil
    import socket
    from datetime import datetime, timedelta
except ImportError as e:
    print(f"Python module missing: {e}")
    sys.exit(1)

# Configuration
TOP_N = 5
BAR_WIDTH = 16
NAME_MAX = 15

def is_wsl():
    """Check if running in WSL"""
    try:
        return 'microsoft' in platform.uname().release.lower()
    except:
        return False

def is_termux():
    """Check if running in Termux"""
    return 'com.termux' in os.environ.get('PREFIX', '')

def human_uptime():
    """Get system uptime"""
    try:
        if platform.system() == "Windows":
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return str(timedelta(seconds=int(uptime.total_seconds())))
        elif platform.system() == "Darwin":
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                boot_timestamp = int(result.stdout.strip().split()[3].strip(','))
                boot_time = datetime.fromtimestamp(boot_timestamp)
                uptime = datetime.now() - boot_time
                return str(timedelta(seconds=int(uptime.total_seconds())))
        else:
            with open("/proc/uptime") as f:
                secs = float(f.read().split()[0])
            return str(timedelta(seconds=int(secs)))
    except:
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return str(timedelta(seconds=int(uptime.total_seconds())))
        except:
            return "Unknown"

def primary_ip():
    """Get primary IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.3)
        if platform.system() == "Windows":
            s.connect(("1.1.1.1", 80))
        else:
            s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        return addr.address
        except:
            pass
        return "127.0.0.1"

def nice_bar(percent, width=BAR_WIDTH):
    """Create progress bar"""
    percent = max(0, min(100, percent))
    filled = int((percent / 100.0) * width)
    return "[" + "█" * filled + "░" * (width - filled) + f"] {percent:5.1f}%"

def short(s, n=NAME_MAX):
    """Truncate string"""
    s = str(s)
    return s if len(s) <= n else s[:n-1] + "…"

def top_processes(n=TOP_N):
    """Get top processes"""
    procs = []
    try:
        # Initialize CPU percentages
        for p in psutil.process_iter(['pid', 'name']):
            try:
                p.cpu_percent(interval=None)
            except:
                pass

        # Small delay for CPU calculation
        import time
        time.sleep(0.05)

        # Collect process info
        for p in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
            try:
                cpu = p.cpu_percent(interval=None)
                mem = p.memory_percent()
                name = p.info.get('name') or p.name()
                
                procs.append({
                    'pid': p.pid,
                    'name': name,
                    'cpu': cpu,
                    'mem': mem
                })
            except:
                continue

        procs.sort(key=lambda x: (x['cpu'], x['mem']), reverse=True)
        return procs[:n]
    except:
        return []

def main():
    try:
        # Get terminal size
        try:
            cols = shutil.get_terminal_size((80, 20)).columns
        except:
            cols = 80

        # System info
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        
        try:
            swap = psutil.swap_memory().percent
        except:
            swap = 0
        
        ip = primary_ip()
        up = human_uptime()
        
        try:
            disk = psutil.disk_usage("/").percent
        except:
            disk = 0

        # Display
        print(f"🕐 {now} | ⏱️  {up}")
        print(f"🌐 {ip} | 💾 {disk:.0f}%")
        print(f"🖥️  CPU: {nice_bar(cpu)}")
        print(f"🧠 RAM: {nice_bar(mem)}")
        if swap > 0:
            print(f"💿 SWAP: {nice_bar(swap)}")

        # Top processes
        procs = top_processes()
        if procs:
            print("\n📊 Top processes:")
            for p in procs:
                print(f"  {p['pid']:6d} {p['cpu']:5.1f}% {p['mem']:5.1f}% {short(p['name'])}")
        else:
            print("\n📊 Top processes: (unavailable)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
PYTHON_EOF

        chmod +x "$DYN_SCRIPT" 2>/dev/null || true
        echo "Created dynamic script at: $DYN_SCRIPT" >&2
    fi
}

# Main execution
main() {
    setup_paths
    create_default_header
    create_dynamic_script

    # Print header
    if [[ -f "$HEADER" ]] && [[ -r "$HEADER" ]]; then
        cat "$HEADER"
        echo
    else
        echo "┌────────────────────────┐"
        echo "│    BLUX GUARD ULTRA    │"
        echo "└────────────────────────┘"
        echo
    fi

    # Run dynamic script
    if [[ -f "$DYN_SCRIPT" ]] && [[ -r "$DYN_SCRIPT" ]]; then
        if check_python_deps; then
            python3 "$DYN_SCRIPT" 2>/dev/null || echo "Dynamic MOTD execution failed"
        else
            echo "🔧 Status: Installing dependencies... (first run)"
            if install_python_deps; then
                python3 "$DYN_SCRIPT" 2>/dev/null || echo "Dynamic MOTD execution failed"
            else
                echo "❌ Status: Install python3 and psutil for full MOTD"
                echo "   Run: pip3 install psutil"
            fi
        fi
    else
        echo "❌ Dynamic MOTD script not found: $DYN_SCRIPT"
    fi

    echo
}

# Run main function
main "$@"
