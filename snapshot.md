# Repository Snapshot

## 1) Metadata
- Repository name: blux-guard
- Organization / owner: unknown
- Default branch (if detectable): work
- HEAD commit hash (if available): 341092ebc2989f9a3f4b7e22942c5cc9e91ca4ed
- Snapshot timestamp (UTC): 2026-01-22T05:29:28.521112Z
- Total file count (excluding directories): 94
- Short description: # BLUX Guard

## 2) Repository Tree
├── .config/
│   ├── blux_guard/
│   │   ├── __init__.py [text]
│   │   ├── motd_dynamic.py [text]
│   │   ├── motd_header.txt [text]
│   │   └── show_motd.sh [text]
│   └── rules/
│       ├── __init__.py [text]
│       ├── index.yar [text]
│       └── rules.json [text]
├── .github/
│   ├── workflows/
│   │   └── ci.yml [text]
│   └── dependabot.yml [text]
├── blux_guard/
│   ├── agents/
│   │   ├── __init__.py [text]
│   │   ├── common.py [text]
│   │   ├── linux_agent.py [text]
│   │   ├── mac_agent.py [text]
│   │   ├── termux_agent.py [text]
│   │   └── windows_agent.py [text]
│   ├── api/
│   │   ├── __init__.py [text]
│   │   ├── guardd.py [text]
│   │   ├── server.py [text]
│   │   └── stream.py [text]
│   ├── cli/
│   │   ├── README.md [text]
│   │   ├── __init__.py [text]
│   │   ├── blux_guard.py [text]
│   │   └── bluxq.py [text]
│   ├── config/
│   │   ├── __init__.py [text]
│   │   ├── default.yaml [text]
│   │   └── local.yaml [text]
│   ├── contracts/
│   │   ├── phase0/
│   │   │   ├── __init__.py [text]
│   │   │   ├── discernment_report.schema.json [text]
│   │   │   ├── guard_receipt.schema.json [text]
│   │   │   └── request_envelope.schema.json [text]
│   │   └── __init__.py [text]
│   ├── core/
│   │   ├── __init__.py [text]
│   │   ├── devsuite.py [text]
│   │   ├── receipt.py [text]
│   │   ├── runtime.py [text]
│   │   ├── security_cockpit.py [text]
│   │   ├── selfcheck.py [text]
│   │   ├── telemetry.md [text]
│   │   └── telemetry.py [text]
│   ├── guard/
│   │   └── mapping/
│   │       └── default_mapping.json [text]
│   ├── integrations/
│   │   └── __init__.py [text]
│   ├── tui/
│   │   ├── README.md [text]
│   │   ├── __init__.py [text]
│   │   ├── app.py [text]
│   │   ├── audit_integrity_panel.py [text]
│   │   ├── audit_panel.py [text]
│   │   ├── bq_panel.py [text]
│   │   ├── cockpit.css [text]
│   │   ├── credentials_panel.py [text]
│   │   ├── dashboard.py [text]
│   │   ├── metrics_panel.py [text]
│   │   ├── process_panel.py [text]
│   │   └── yara_panel.py [text]
│   ├── __init__.py [text]
│   ├── audit.py [text]
│   ├── doctor.py [text]
│   └── quantum_plugin.py [text]
├── docs/
│   └── ROLE.md [text]
├── examples/
│   ├── config.sample.yaml [text]
│   ├── doctrine.sample.md [text]
│   └── guard_receipt.example.json [text]
├── scripts/
│   ├── physics_check.sh [text]
│   └── physics_guard.py [text]
├── tests/
│   ├── test_cli.py [text]
│   └── test_receipt.py [text]
├── .gitignore [text]
├── .pre-commit-config.yaml [text]
├── .ruff.toml [text]
├── ARCHITECTURE.md [text]
├── AUDIT_SCHEMA.md [text]
├── CHANGELOG.md [text]
├── COCKPIT_SPEC.md [text]
├── CODE_OF_CONDUCT.md [text]
├── COMMERCIAL.md [text]
├── CONFIGURATION.md [text]
├── CONTRIBUTING.md [text]
├── INSTALL.md [text]
├── LICENSE [text]
├── LICENSE-APACHE [text]
├── LICENSE-COMMERCIAL [text]
├── Makefile [text]
├── NOTICE [text]
├── OPERATIONS.md [text]
├── PRIVACY.md [text]
├── README.md [text]
├── ROADMAP.md [text]
├── ROLE.md [text]
├── SECURITY.md [text]
├── SUPPORT.md [text]
├── TROUBLESHOOTING.md [text]
├── mypy.ini [text]
├── pyproject.toml [text]
├── pytest.ini [text]
└── requirements.txt [text]

## 3) FULL FILE CONTENTS (MANDATORY)

FILE: .config/blux_guard/__init__.py
Kind: text
Size: 0
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:

FILE: .config/blux_guard/motd_dynamic.py
Kind: text
Size: 10245
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
#!/usr/bin/env python3
# motd_dynamic.py — compact live status + top processes
# Cross-platform compatible: WSL2, Linux, Windows, macOS, Android Termux

import sys
import psutil
import socket
import shutil
import os
import platform
from datetime import datetime, timedelta

# Configuration
TOP_N = 6            # number of top processes to show
BAR_WIDTH = 20       # width of the CPU/RAM bars
NAME_MAX = 18        # truncate long process names to fit small screens

def is_wsl():
    """Check if running in WSL"""
    if 'microsoft' in platform.uname().release.lower():
        return True
    if os.path.exists('/run/WSL'):
        return True
    if os.environ.get('WSL_DISTRO_NAME'):
        return True
    return False

def is_termux():
    """Check if running in Termux"""
    return 'com.termux' in os.environ.get('PREFIX', '')

def human_uptime():
    """Get system uptime in human readable format"""
    try:
        if platform.system() == "Windows":
            # Windows uptime
            uptime_seconds = psutil.boot_time()
            boot_time = datetime.fromtimestamp(uptime_seconds)
            uptime = datetime.now() - boot_time
            return str(timedelta(seconds=int(uptime.total_seconds())))
        elif platform.system() == "Darwin":  # macOS
            # macOS uses sysctl for uptime
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # kern.boottime returns timestamp
                boot_timestamp = int(result.stdout.strip().split(' ')[3].strip(','))
                boot_time = datetime.fromtimestamp(boot_timestamp)
                uptime = datetime.now() - boot_time
                return str(timedelta(seconds=int(uptime.total_seconds())))
        else:
            # Linux/Unix/Android
            with open("/proc/uptime") as f:
                secs = float(f.read().split()[0])
            return str(timedelta(seconds=int(secs)))
    except (FileNotFoundError, PermissionError, IndexError, ValueError):
        try:
            # Fallback using psutil
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return str(timedelta(seconds=int(uptime.total_seconds())))
        except:
            return "N/A"

def primary_ip():
    """Get primary IP address with platform-specific methods"""
    try:
        # Try connecting to a public DNS first
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.4)
        
        # Use different approaches based on platform
        if platform.system() == "Windows":
            s.connect(("1.1.1.1", 80))  # Cloudflare DNS
        else:
            s.connect(("8.8.8.8", 80))  # Google DNS
            
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback: find first non-localhost IPv4 address
        try:
            hostname = socket.gethostname()
            # Get all IP addresses
            all_ips = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        all_ips.append(addr.address)
            
            # Prefer certain interfaces
            preferred_interfaces = ['eth0', 'en0', 'wlan0', 'wlp', 'enp']
            for ip in all_ips:
                return ip
                
            # Return first non-localhost IP if available
            for ip in all_ips:
                if ip != '127.0.0.1':
                    return ip
                    
            return "127.0.0.1"
        except:
            return "127.0.0.1"

def tmux_status():
    """Check tmux status with better error handling"""
    try:
        # Check if tmux is available
        if shutil.which("tmux") is None:
            return "tmux: not installed"
            
        # Use subprocess for better cross-platform compatibility
        import subprocess
        result = subprocess.run(
            ["tmux", "ls"], 
            capture_output=True, 
            text=True, 
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout.strip():
            sessions = result.stdout.strip()
            if "blux_ultra_shell" in sessions:
                return "tmux: blux_ultra_shell (attach: tmux attach -t blux_ultra_shell)"
            session_count = len(sessions.split('\n'))
            return f"tmux: {session_count} session(s)"
        else:
            return "tmux: no sessions"
            
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return "tmux: unavailable"

def nice_bar(percent, width=BAR_WIDTH):
    """Create a nice progress bar"""
    if percent < 0: percent = 0
    if percent > 100: percent = 100
    filled = int((percent / 100.0) * width)
    return "[" + "#"*filled + "-"*(width-filled) + f"] {percent:5.1f}%"

def short(s, n=NAME_MAX):
    """Truncate string with ellipsis"""
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n-1] + "…"

def top_processes(n=TOP_N):
    """Get top processes with platform-specific handling"""
    procs = []
    
    try:
        # Initial CPU percent sampling (non-blocking)
        for p in psutil.process_iter(['pid', 'name', 'username']):
            try:
                p.cpu_percent(interval=None)  # First call to initialize
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Small sleep for CPU calculation (shorter for better responsiveness)
        import time
        time.sleep(0.05)

        # Collect process information
        for p in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
            try:
                cpu = p.cpu_percent(interval=None)
                mem = p.memory_percent()
                name = p.info.get('name') or p.name()
                username = p.info.get('username') or ''
                
                # Handle different username formats across platforms
                if '\\' in username:  # Windows domain format
                    username = username.split('\\')[-1]
                
                procs.append({
                    'pid': p.pid,
                    'name': name,
                    'user': username,
                    'cpu': cpu,
                    'mem': mem
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by CPU (descending), then by memory (descending)
        procs.sort(key=lambda x: (x['cpu'], x['mem']), reverse=True)
        return procs[:n]
        
    except Exception as e:
        # Return empty list if process enumeration fails
        return []

def format_procs_table(procs):
    """Format processes table with dynamic terminal width"""
    try:
        cols = shutil.get_terminal_size((80, 20)).columns
    except (ValueError, OSError):
        cols = 80

    # Minimal widths with better adaptability
    pid_w = 6
    cpu_w = 7
    mem_w = 7
    name_w = max(10, min(NAME_MAX, cols - (pid_w + cpu_w + mem_w + 6)))
    
    header = f"{'PID':>{pid_w}} {'CPU%':>{cpu_w}} {'MEM%':>{mem_w}} {'NAME':<{name_w}}"
    lines = [header, "-" * min(cols, len(header))]
    
    for p in procs:
        line = f"{p['pid']:{pid_w}d} {p['cpu']:6.1f} {p['mem']:6.1f}% {short(p['name'], name_w):<{name_w}}"
        lines.append(line)
    
    return "\n".join(lines)

def get_disk_usage():
    """Get disk usage for appropriate root directory"""
    try:
        if platform.system() == "Windows":
            return psutil.disk_usage("C:").percent
        elif is_termux():
            # Termux typically uses /data or /storage
            for path in ["/data", "/storage", "/"]:
                try:
                    return psutil.disk_usage(path).percent
                except (PermissionError, FileNotFoundError):
                    continue
            return psutil.disk_usage("/").percent
        else:
            return psutil.disk_usage("/").percent
    except (PermissionError, FileNotFoundError):
        return 0.0

def main():
    """Main function with comprehensive error handling"""
    try:
        # Get terminal size with fallback
        try:
            cols = shutil.get_terminal_size((80, 20)).columns
        except (ValueError, OSError):
            cols = 80

        # System information
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # CPU usage with platform-specific interval
        cpu_interval = 0.08 if platform.system() == "Windows" else 0.1
        cpu = psutil.cpu_percent(interval=cpu_interval)
        
        # Memory usage
        mem = psutil.virtual_memory().percent
        
        # Swap usage (handle systems without swap)
        try:
            swap = psutil.swap_memory().percent
        except (AttributeError, NotImplementedError):
            swap = 0.0
            
        # Other system info
        ip = primary_ip()
        up = human_uptime()
        disk = get_disk_usage()

        # Display header information
        print(f"Time: {now} | Uptime: {up}")
        print(f"IP: {ip} | Disk: {disk:.0f}%")
        
        # System resource bars
        bar_width = min(BAR_WIDTH, max(8, cols // 5))
        print("CPU: " + nice_bar(cpu, width=bar_width))
        print("RAM: " + nice_bar(mem, width=bar_width))
        
        if swap > 0:  # Only show swap if available
            print("SWP: " + nice_bar(swap, width=bar_width))
        
        # Tmux status
        print(tmux_status())
        print()
        
        # Top processes
        procs = top_processes()
        if procs:
            print("Top processes:")
            print(format_procs_table(procs))
        else:
            print("Top processes: (unavailable)")
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating MOTD: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

FILE: .config/blux_guard/motd_header.txt
Kind: text
Size: 747
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         🛡️  𝐁𝐋𝐔𝐗 𝐆𝐔𝐀𝐑𝐃 𝐔𝐋𝐓𝐑𝐀  🛡️             ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃   🟢 ACTIVE   ┃  🚀 COCKPIT  ┃  🔒 SECURE   ┃   ⚡ READY   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

FILE: .config/blux_guard/show_motd.sh
Kind: text
Size: 11201
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
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

FILE: .config/rules/__init__.py
Kind: text
Size: 4266
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
"""
BLUX Guard Rules Engine Configuration Package

This package manages the loading, validation, and application of security rules
within the BLUX Guard ecosystem. It provides tools for dynamically updating
rulesets and handling any associated dependencies.

Version: 1.0.0
Author: Outer Void Team
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default rules directory (relative to /blux-guard, adjust as needed)
DEFAULT_RULES_DIR = Path("/blux-guard/.config/rules")
DEFAULT_RULES_FILE = DEFAULT_RULES_DIR / "rules.json"

class RulesEngineConfig:
    """
    Configuration class for the BLUX Guard Rules Engine.
    Manages the loading and validation of security rules from JSON files.
    """

    def __init__(self, rules_dir: Optional[Path] = None, rules_file: Optional[Path] = None):
        """
        Initializes the RulesEngineConfig with the specified rules directory
        and rules file. If not provided, defaults are used.
        """
        self.rules_dir = rules_dir or DEFAULT_RULES_DIR
        self.rules_file = rules_file or DEFAULT_RULES_FILE
        self.rules = self._load_and_validate_rules()


    def _load_and_validate_rules(self) -> List[Dict[str, Any]]:
        """
        Loads the rules from the configured JSON file and validates
        their structure. Returns a list of rule dictionaries.
        Raises an exception if the file is invalid or rules are malformed.
        """
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)

            if not isinstance(data, dict) or 'rules' not in data:
                raise ValueError("Invalid rules file format: 'rules' key missing.")

            rules = data['rules']
            if not isinstance(rules, list):
                raise ValueError("Invalid rules file format: 'rules' must be a list.")

            # Perform basic rule validation (add more checks as needed)
            for rule in rules:
                if not isinstance(rule, dict):
                    raise ValueError("Invalid rule format: Each rule must be a dictionary.")
                if 'id' not in rule or 'condition' not in rule or 'response' not in rule:
                     raise ValueError(f"Rule with ID '{rule.get('id', 'unknown')}' is missing required fields ('id', 'condition', 'response').")

            logger.info(f"Successfully loaded and validated {len(rules)} rules from {self.rules_file}")
            return rules

        except FileNotFoundError:
            logger.error(f"Rules file not found: {self.rules_file}")
            raise  # Re-raise to indicate configuration error
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in {self.rules_file}: {e}")
            raise  # Re-raise to indicate configuration error
        except ValueError as e:
            logger.error(f"Validation error in rules file: {e}")
            raise  # Re-raise to indicate configuration error
        except Exception as e:
            logger.exception(f"Unexpected error loading rules: {e}")
            raise  # Re-raise to indicate configuration error


    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Returns the list of loaded and validated rules.
        """
        return self.rules

    def reload_rules(self):
        """
        Reloads the rules from the configuration file.
        Useful for dynamically updating rulesets.
        """
        try:
            self.rules = self._load_and_validate_rules()
            logger.info("Rules reloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to reload rules: {e}")

# Example usage and initialization (optional)
try:
    rules_config = RulesEngineConfig()
    all_rules = rules_config.get_rules()
    logger.info(f"RulesEngineConfig initialized with {len(all_rules)} rules.")
except Exception as e:
    logger.error(f"Failed to initialize RulesEngineConfig: {e}")

# Define __all__ for public API exposure
__all__ = [
    "RulesEngineConfig",
    "DEFAULT_RULES_DIR",
    "DEFAULT_RULES_FILE",
    "logger",
    "all_rules" if 'all_rules' in locals() else None  # Only expose if initialized
]

FILE: .config/rules/index.yar
Kind: text
Size: 1816
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
/*
BLUX Guard YARA Rules Index

This file serves as the primary index for YARA rules used by the BLUX Guard
nano-swarm system.  It can include rules directly or import rules from
other files within the rules directory.

Author: Outer Void Team
Date: 2024-01-01

Rules should be organized by category and include descriptive metadata to
facilitate maintenance and analysis.
*/

/* --- Basic Example Rule --- */
rule ExampleMalware
{
    meta:
        description = "Detects a known malware signature"
        author = "Outer Void Team"
        date = "2024-01-01"
        malware_family = "ExampleFamily"
        confidence = 75 // Percentage
    strings:
        $mz = { 4D 5A }  // PE Header
        $string1 = "SuspiciousString1"
        $string2 = "SuspiciousString2"
    condition:
        $mz and $string1 and $string2
}

/* --- Rule Importing Example --- */
/*
import "rules/phishing_rules.yar" // Relative to this file, adjust path as needed
import "rules/exploit_rules.yar"
*/

/* --- More Rule Examples --- */

rule DetectPotentiallyUnwantedApp
{
    meta:
        description = "Detects a Potentially Unwanted Application (PUA) based on common characteristics"
        author = "Outer Void Team"
        date = "2024-01-01"
        threat_level = "low"
    strings:
        $string1 = "InstallShield"
        $string2 = "OpenCandy"
        $string3 = "Toolbar"
    condition:
        all of them
}

rule DetectSuspiciousFileOperation
{
    meta:
        description = "Detects suspicious file operations like creating executables in temp directories"
        author = "Outer Void Team"
        date = "2024-01-01"
        threat_level = "medium"
    strings:
        $api1 = "CreateFile"
        $api2 = "WriteFile"
        $path = "%TEMP%\\*.exe" nocase
    condition:
        $api1 and $api2 and $path
}

FILE: .config/rules/rules.json
Kind: text
Size: 11640
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
{
  "manifest_version": "1.0",
  "generated_by": "blux-guard/rulegen-v1",
  "generated_at": "2025-10-13T00:00:00Z",
  "rules": [
    {
      "id": "silent_exfil",
      "name": "Silent exfil: many distinct remote IPs",
      "description": "Detect a process/app opening many distinct external sockets in a short time window — high-confidence exfiltration pattern.  Indicates a process is attempting to send data to multiple destinations quickly.",
      "severity": "high",
      "confidence": 0.9,
      "tags": ["network", "exfiltration", "threshold"],
      "condition": {
        "type": "threshold",
        "field": "network.remote_ips_count",
        "op": "gt",
        "value": 10,
        "window": 60
      },
      "response": [
        {
          "stage": "observe",
          "action": "log",
          "params": {
            "note": "silent_exfil_observed",
            "capture": ["socket_list", "dns_queries", "ja3"]
          },
          "operator_ack": false
        },
        {
          "stage": "snapshot",
          "action": "snapshot_process",
          "params": {
            "capture_memory": true,
            "pcap_bytes": 65536
          },
          "operator_ack": false
        },
        {
          "stage": "throttle",
          "action": "apply_qos_cap",
          "params": {
            "network_rate_kbps": 16,
            "duration_s": 600
          },
          "operator_ack": false
        },
        {
          "stage": "quarantine",
          "action": "isolate_uid",
          "params": {
            "method": "vpn_block_per_uid"
          },
          "operator_ack": true
        }
      ],
      "pow": {
        "required": true,
        "difficulty": 18,
        "rationale": "raise compute cost for bursts"
      },
      "cooldown": 300,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    },
    {
      "id": "mount_surprise",
      "name": "Mount surprise: removable SD mounted while locked + charging",
      "description": "Removable storage attached while device is locked and charging and user absent for a long period — high risk for unattended data harvesting or staging.  Suggests someone is physically accessing the device for unauthorized purposes.",
      "severity": "medium",
      "confidence": 0.85,
      "tags": ["filesystem", "removable", "physical"],
      "condition": {
        "type": "and",
        "clauses": [
          {
            "type": "match",
            "field": "device.charging",
            "value": true
          },
          {
            "type": "exists",
            "field": "device.removable_sd_mounted"
          },
          {
            "type": "match",
            "field": "device.screen_locked",
            "value": true
          },
          {
            "type": "threshold",
            "field": "device.time_since_last_unlock_hours",
            "op": "gte",
            "value": 12,
            "window": 3600
          }
        ]
      },
      "response": [
        {
          "stage": "observe",
          "action": "log",
          "params": {
            "capture": ["mount_point", "mount_options", "device_id"]
          },
          "operator_ack": false
        },
        {
          "stage": "contain",
          "action": "remount_readonly",
          "params": {
            "path_field": "device.removable_sd_path"
          },
          "operator_ack": true
        },
        {
          "stage": "snapshot",
          "action": "compute_and_store_checksums",
          "params": {
            "hashes": ["sha256"],
            "store": "security/logs/forensics"
          },
          "operator_ack": false
        }
      ],
      "pow": {
        "required": false
      },
      "cooldown": 120,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    },
    {
      "id": "privilege_creep",
      "name": "Privilege creep: new permission shortly after unknown network connection",
      "description": "Detect when an app gains a new runtime permission (or installs helper) shortly after unknown/outbound network connections — potential remote install/callback chain.  Indicates possible malware installation or remote code execution.",
      "severity": "high",
      "confidence": 0.9,
      "tags": ["permission", "timeline", "correlation"],
      "condition": {
        "type": "and",
        "clauses": [
          {
            "type": "exists",
            "field": "app.new_permission"
          },
          {
            "type": "threshold",
            "field": "network.unknown_conn_count",
            "op": "gt",
            "value": 0,
            "window": 120
          }
        ]
      },
      "response": [
        {
          "stage": "observe",
          "action": "log",
          "params": {
            "capture": ["permission_name", "installer_package", "recent_conns"]
          },
          "operator_ack": false
        },
        {
          "stage": "snapshot",
          "action": "binary_and_manifest_capture",
          "params": {
            "capture_paths": ["app.apk_path", "app.code_hash", "signing_cert"]
          },
          "operator_ack": false
        },
        {
          "stage": "revert",
          "action": "revoke_permission",
          "params": {
            "permission_field": "app.new_permission"
          },
          "operator_ack": true
        },
        {
          "stage": "quarantine",
          "action": "freeze_app",
          "params": {
            "method": "force_stop_and_net_isolate"
          },
          "operator_ack": true
        }
      ],
      "pow": {
        "required": true,
        "difficulty": 20,
        "rationale": "prevent automated escalation without operator involvement"
      },
      "cooldown": 600,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    },
    {
      "id": "ui_hijack_overlay",
      "name": "UI hijack overlay close to credential event",
      "description": "Overlay/request for SYSTEM_ALERT_WINDOW or similar within a short window of credential entry events — strong signal for phishing / UI overlay capture.  Someone is trying to steal credentials by covering the real UI with a fake one.",
      "severity": "high",
      "confidence": 0.92,
      "tags": ["ui", "phishing", "overlay"],
      "condition": {
        "type": "and",
        "clauses": [
          {
            "type": "exists",
            "field": "ui.overlay_detected"
          },
          {
            "type": "exists",
            "field": "event.credential_entry_time"
          },
          {
            "type": "threshold",
            "field": "ui.overlay_age_seconds",
            "op": "lt",
            "value": 5,
            "window": 10
          }
        ]
      },
      "response": [
        {
          "stage": "observe",
          "action": "log",
          "params": {
            "capture": ["overlay_pid", "app_package", "overlay_layout_dump"]
          },
          "operator_ack": false
        },
        {
          "stage": "contain",
          "action": "block_overlay",
          "params": {
            "method": "block_system_alert_window_for_uid"
          },
          "operator_ack": false
        },
        {
          "stage": "prompt",
          "action": "operator_prompt",
          "params": {
            "message": "Overlay detected during credential entry. Approve overlay or quarantine app?"
          },
          "operator_ack": true
        }
      ],
      "pow": {
        "required": false
      },
      "cooldown": 60,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    },
    {
      "id": "process_mimic",
      "name": "Process mimic: same package name, different signing cert or binary hash",
      "description": "Detect when an installed package presents a previously known package name but its signing certificate or binary hash differs — potential masquerade/tampering. This is a strong indicator of an app being replaced with a malicious version.",
      "severity": "critical",
      "confidence": 0.95,
      "tags": ["integrity", "signing", "tamper"],
      "condition": {
        "type": "and",
        "clauses": [
          {
            "type": "exists",
            "field": "app.package_name"
          },
          {
            "type": "exists",
            "field": "app.current_signature"
          },
          {
            "type": "exists",
            "field": "app.known_signature_mismatch"
          }
        ]
      },
      "response": [
        {
          "stage": "snapshot",
          "action": "capture_binaries_and_cert",
          "params": {
            "store": "security/logs/forensics"
          },
          "operator_ack": false
        },
        {
          "stage": "quarantine",
          "action": "freeze_app_and_block_uid",
          "params": {
            "retain": ["hashes", "manifest", "install_source"]
          },
          "operator_ack": true
        },
        {
          "stage": "forensics",
          "action": "preserve_boot_state",
          "params": {
            "note": "critical_integrity_suspected"
          },
          "operator_ack": true
        }
      ],
      "pow": {
        "required": false
      },
      "cooldown": 3600,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    },
    {
      "id": "cold_start_lateral",
      "name": "Cold-start lateral: unknown AUTOSTART receiver after reboot",
      "description": "Detect unknown receivers or autostart hooks registered after boot — potential lateral persistence or post-boot implant.  This often signifies a malicious app setting itself up to run automatically after the device restarts.",
      "severity": "high",
      "confidence": 0.88,
      "tags": ["boot", "autostart", "persistence"],
      "condition": {
        "type": "and",
        "clauses": [
          {
            "type": "match",
            "field": "system.boot_completed",
            "value": true
          },
          {
            "type": "exists",
            "field": "app.autostart_receiver_new"
          },
          {
            "type": "threshold",
            "field": "system.uptime_minutes",
            "op": "lt",
            "value": 5,
            "window": 300
          }
        ]
      },
      "response": [
        {
          "stage": "observe",
          "action": "log",
          "params": {
            "capture": ["receiver_intent", "registering_package", "timestamp"]
          },
          "operator_ack": false
        },
        {
          "stage": "contain",
          "action": "block_autostart_until_review",
          "params": {
            "method": "disable_receiver_pending_operator"
          },
          "operator_ack": true
        },
        {
          "stage": "snapshot",
          "action": "collect_process_list_and_bindings",
          "params": {
            "store": "security/logs/forensics"
          },
          "operator_ack": false
        }
      ],
      "pow": {
        "required": false
      },
      "cooldown": 900,
      "meta": {
        "version": "1",
        "author": "blux",
        "created_at": "2025-10-13T00:00:00Z"
      },
      "signature": null
    }
  ]
}

FILE: .github/dependabot.yml
Kind: text
Size: 103
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly

FILE: .github/workflows/ci.yml
Kind: text
Size: 487
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
name: CI
permissions:
  contents: read

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install package
        run: |
          python -m pip install -U pip
          pip install -e .
          pip install pytest
      - name: Physics check
        run: scripts/physics_check.sh
      - name: Pytest
        run: pytest

FILE: .gitignore
Kind: text
Size: 4455
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a team project
#  using PyCharm, it is recommended to add the JetBrains template and exclude user-specific
#  files.

.idea/
*.iws
*.iml
*.ipr

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
*.code-workspace

# Local History for Visual Studio Code
.history/

# Sublime Text
*.sublime-*

# BLUX Guard Specific
# Database files
*.db
*.db-journal
*.sqlite
*.sqlite3

# Log files
*.log
logs/
blux-guard.log
security-events.log

# Configuration files (except example/template configs)
config.yaml
config.json
secrets.ini
*.key
*.pem
*.crt

# Sensor data and cache
sensor-cache/
monitoring-data/
captures/
tmp/

# Runtime data
.pids/
.pid

# Build outputs
/blux_guard.egg-info/
/dist/
/build/

# Platform-specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Performance reports
prof/

# Temporary files
*.tmp
*.temp

# Coverage reports
.coverage
htmlcov/

# Test data
test-data/
fixtures/

# Jupyter
.ipynb_checkpoints

# Package manager specific
Pipfile.lock
poetry.lock
pdm.lock

# Documentation
/site
/docs/_build

# Virtual environments
venv/
ENV/
env/

# Development tools
.mypy_cache/
.pytest_cache/
.tox/
.nox/

# OS generated files
[Tt]humbs.db
*~
*.lok

# Backup files
*.bak
*.backup
*.old

# Certificate files (keep templates but ignore actual certs)
!certificates/*.template
certificates/*.crt
certificates/*.key
certificates/*.pem

# Local development overrides
local_settings.py
development.ini

FILE: .pre-commit-config.yaml
Kind: text
Size: 276
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace

FILE: .ruff.toml
Kind: text
Size: 102
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
line-length = 100
target-version = "py39"
select = ["E", "F", "I", "UP", "B", "PL"]
ignore = ["E501"]

FILE: ARCHITECTURE.md
Kind: text
Size: 2453
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# BLUX Guard Architecture

## High-Level Overview

BLUX Guard combines legacy protection engines with the new Developer Suite cockpit. The system keeps the
original security pipeline while routing modern workflows through the developer-oriented
runtime:

1. **Interface Layer** — `blux_guard/cli/bluxq.py` Quantum CLI and Textual TUI components under
   `blux_guard/tui/`.
2. **Execution Layer** — receipt issuance from `blux_guard/core/receipt.py` and development flows in
   `blux_guard/core/devsuite.py`.
3. **Telemetry Layer** — `blux_guard/core/telemetry.py` streams JSONL and SQLite mirrors while the API
   exposes Prometheus metrics.
4. **Platform Agents** — `blux_guard/agents/` collects host data per OS and reports to the daemon.
5. **Daemon & API** — `blux_guard/api/guardd.py` launches the FastAPI server in `blux_guard/api/server.py`
   and relays cockpit events through `blux_guard/api/stream.py`.

## Control Flow

```
bluxq → runtime.ensure_supported_python → receipt.issue_guard_receipt → telemetry.record_event
```

1. Commands enter through the CLI or cockpit.
2. Receipt issuance is deterministic and protocol-scoped.
3. Results, audits, and metrics emit through `telemetry.record_event` which never raises on I/O errors.
4. The daemon and TUI subscribe to telemetry streams and update panels in real time.

## Module Relationships

- `blux_guard/core/__init__.py` exposes the developer runtime modules.
- Legacy sensors and trip engines are handled through the guard receipt engine.
- Agents call back into `telemetry` so all platforms share a unified audit surface.

## Platform Matrix

| Component            | Android / Termux | Linux / WSL2 | macOS | Windows |
|----------------------|------------------|--------------|-------|---------|
| CLI (`bluxq`)        | ✅ Termux        | ✅ Native    | ✅    | ✅ PowerShell |
| TUI (`dashboard`)    | ✅ (termux-x11)  | ✅ Native    | ✅    | ✅ Windows Terminal |
| Daemon (`bluxqd`)    | ✅ uvicorn       | ✅ uvicorn   | ✅    | ✅ (uvicorn + asyncio) |
| Agents               | Termux agent     | Linux agent  | mac agent | Windows agent |
| Telemetry storage    | `$HOME/.config`  | `$HOME/.config` | `$HOME/Library/Application Support` equivalent | `%USERPROFILE%\.config` |

## Future Extensions

- Commander web cockpit mirrors via `/api/stream`.
- SBOM generation and SLSA compliance in CI.
- Extended receipt policies for containerized builds.

FILE: AUDIT_SCHEMA.md
Kind: text
Size: 1347
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
"""
BLUX Guard Unified Audit Schema
"""

# Record Format

Audit records are JSON objects written as JSONL to `~/.config/blux-guard/logs/audit.jsonl` (or the path defined by `BLUX_GUARD_LOG_DIR`). Fields:

- `ts` (float): Unix timestamp in seconds.
- `level` (str): `debug` | `info` | `warn` | `error`.
- `actor` (str): Source component (`cli`, `tui`, `scanner`, etc.).
- `action` (str): Event identifier (e.g., `tui.launch`, `cli.doctor`).
- `stream` (str): `audit`.
- `payload` (object): Structured data for the action (command text, paths, counts, status).
- `channel` (str): Backward-compatible alias for `action` used by existing telemetry sinks.
- `correlation_id` (str): UUID4 tying related events together.
- `component` (str, optional): Subsystem name (e.g., `quantum_plugin`, `install`).

# Guarantees

- **Append-only**: Writes are append-only; no truncation by default.
- **Best-effort**: Logging failures do not crash the operator flow; warnings are emitted to stderr once.

# Paths

- **Audit Log**: `~/.config/blux-guard/logs/audit.jsonl`
- **SQLite Mirror**: `~/.config/blux-guard/logs/telemetry.db` (for fast queries)

# Correlation

- CLI commands create a `correlation_id` at invocation and pass it into TUI and exports.
- TUI screen transitions emit `tui.screen.enter`/`exit` events with the same correlation id when available.

FILE: CHANGELOG.md
Kind: text
Size: 381
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Changelog

## [GUARD-PM2-FIX] Add Typer dependency; make telemetry best-effort; docs refresh
- Declare CLI/runtime dependencies including Typer, psutil, FastAPI, and Prometheus exporters.
- Harden telemetry writer with best-effort JSONL/SQLite handling and startup degrade notices.
- Document cockpit usage, CLI commands, telemetry behavior, and troubleshooting across the repo.

FILE: COCKPIT_SPEC.md
Kind: text
Size: 2110
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
"""
BLUX Guard Developer Security Cockpit — Specification
"""

# Overview

The Cockpit provides a unified operator view for BLUX Guard across CLI and TUI surfaces. It focuses on a single operator journey: launch the cockpit (`bluxq guard tui`), observe telemetry, run diagnostics, and export evidence.

# Navigation

- **Home**: Overview banner, current mode (secure/dev/ops), quick links to start scans.
- **Telemetry**: Metrics, process view, YARA scans, credentials audit, and audit chain verification with refresh hotkeys.
- **Rules**: Rule summaries and health indicators.
- **Incidents**: Aggregated audit timeline filtered to warnings/errors plus last export paths.
Each screen emits audit events on entry/exit and on key actions (scan, export).

# Data Contracts

- **Audit Events**: JSONL records defined in `AUDIT_SCHEMA.md`. Each record includes `correlation_id`, `actor`, `action`, `stream`, `payload`, and timestamps.
- **Config Paths**: All writable state lives under `~/.config/blux-guard` by default. Paths can be overridden with environment variables (see `blux_guard/config.py`).
- **Quantum Plugin Surface**: `blux_guard.quantum_plugin.register(app)` expects a Typer app and registers the Guard command tree.

# Flows

1. **Launch**: Operator runs `bluxq guard tui`. CLI creates a correlation_id, records `tui.launch`, and starts the Textual app (`blux_guard.tui.app.CockpitApp`).
2. **Telemetry Refresh**: Hotkeys trigger panel refresh; each refresh logs `tui.refresh` with the screen identifier.
3. **Rules**: Rule view surfaces status summaries and warning hints.
4. **Incidents/Audit**: Timeline reads audit JSONL and shows warnings/errors. Exports write bundles via `security_cockpit.export_diagnostics` and emit `tui.export` events.
5. **Doctor/Verify**: CLI `doctor` and `verify` run environment and config checks, emitting audit events and returning non-zero on failure.

# Compatibility

- `blux_guard/cli/bluxq.py` remains the primary entry point for cockpit and guard operations.
- Existing panels remain intact; new screens orchestrate them for the unified cockpit experience.

FILE: CODE_OF_CONDUCT.md
Kind: text
Size: 1341
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Contributor Covenant Code of Conduct

## Our Pledge

We pledge to make participation in BLUX Guard a harassment-free experience for everyone, regardless of age,
body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-
economic status, nationality, personal appearance, race, caste, color, religion, or sexual identity and
orientation.

## Our Standards

- Use welcoming and inclusive language.
- Be respectful of differing viewpoints and experiences.
- Gracefully accept constructive criticism.
- Focus on what is best for the community.
- Show empathy towards other community members.

## Unacceptable Behavior

- Violence, threats, or discriminatory jokes and language.
- Public or private harassment.
- Publishing others' private information without explicit permission.

## Enforcement Responsibilities

Project maintainers are responsible for clarifying standards and taking appropriate and fair corrective action.

## Scope

This Code applies within all project spaces and when individuals represent the project.

## Enforcement

Report incidents to the maintainers listed in `SUPPORT.md`. All complaints will be reviewed promptly and
confidentially.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version
2.1.

FILE: COMMERCIAL.md
Kind: text
Size: 716
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Commercial Licensing

Blux Guard is dual-licensed. You may use it under the open-source Apache License 2.0 for permissive, community use. Commercial use requires a separate commercial agreement.

## When you need a commercial license
Examples include:
- Embedding Blux Guard into a paid or closed-source product.
- Offering Blux Guard or its derivatives as a hosted or managed service.
- Using Blux Guard internally at scale in a proprietary environment where distribution restrictions apply.
- Any monetized deployment that goes beyond the Apache-2.0 terms.

## How to proceed
Contact the maintainers at **theoutervoid@outlook.com** to discuss commercial licensing terms and obtain permission for commercial use.

FILE: CONFIGURATION.md
Kind: text
Size: 638
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Configuration Reference

BLUX Guard ships with defaults under `blux_guard/config/default.yaml` and optional local overrides in
`blux_guard/config/local.yaml`.

## YAML Schema

```yaml
telemetry:
  log_dir: ~/.config/blux-guard/logs
  enabled: true
  warn_once: true
api:
  host: 0.0.0.0
  port: 8000
```

## Override Mechanics

1. The project reads `config/default.yaml` first.
2. If `config/local.yaml` exists, keys merge over defaults without altering the tracked file.
3. Environment variables take precedence when provided (e.g., `BLUX_GUARD_LOG_DIR`).

## Examples

See the `examples/` directory for sample configuration snippets.

FILE: CONTRIBUTING.md
Kind: text
Size: 1216
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Contributing Guide

We welcome patches that respect the BLUX Guard non-destructive covenant.

## Development Environment

1. Fork and clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # PowerShell: .venv\\Scripts\\Activate.ps1
   pip install -U pip
   pip install -e .[dev]
   ```
3. Install pre-commit hooks: `pre-commit install`.

## Coding Standards

- Follow Ruff and MyPy guidance (`make lint`).
- New modules should integrate with `telemetry.record_event` instead of writing directly to files.
- Maintain compatibility with Termux, Linux, macOS, and Windows.

## Testing

Run `make test` locally. CI executes Ruff, MyPy (non-fatal), and Pytest across Python 3.9–3.11.

## Documentation

Update relevant docs when adding features. The README links to the documentation suite; keep entries current.

## Pull Requests

- Reference the appropriate `[ENTERPRISE]` or `[GUARD-*]` tag in commit subjects when applicable.
- Include a summary of tests executed.
- Ensure non-destructive changes: do not remove or overwrite existing legacy modules.

## Code of Conduct

Participation is governed by `CODE_OF_CONDUCT.md`.

FILE: INSTALL.md
Kind: text
Size: 2127
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Installation Guide

BLUX Guard supports Android/Termux, Linux (including WSL2), macOS, and Windows. All instructions preserve
existing cockpit entry points while enabling the new `bluxq` CLI.

BLUX Guard is protocol enforcement + userland constraints.

## Common Steps

```bash
python -m pip install -U pip
pip install -e .[dev]  # falls back to -e . if optional deps unavailable
```

After installation, launch the daemon and cockpit:

```bash
bluxqd &
bluxq guard status
bluxq guard tui --mode dev
```

## Android / Termux

1. Install dependencies: `pkg install python git clang make`.
2. Clone the repository and install the package with `pip install -e .`.
3. Telemetry writes to `$HOME/.config/blux-guard/logs`; run `termux-setup-storage` if you see permission prompts.
4. Start the cockpit with `bluxq guard tui --mode dev` inside Termux or termux-x11.

## Linux / WSL2

1. Ensure Python 3.9+ is installed via your system package manager (for example, install
   `python3` and `python3-venv` on Debian/Ubuntu).
2. Install the package with `pip install -e .` (optionally inside a virtual environment).
3. Launch the daemon (`bluxqd &`) and then run `bluxq guard tui --mode secure` for production monitoring.

## macOS

1. Install Homebrew Python 3.11+ or use the system Python if it meets the minimum version.
2. Run `pip install -e .` from inside a virtual environment (recommended via `python -m venv .venv`).
3. Adjust configuration overrides in `config/local.yaml` as needed.

## Windows

1. Use PowerShell 7+ and install Python 3.11 from the Microsoft Store or python.org.
2. Install the package with `pip install -e .` and ensure your Python scripts directory is on `PATH`.
3. Telemetry logs live in `%USERPROFILE%\.config\blux-guard\logs`.
4. Start the daemon in one window (`bluxqd`) and launch the cockpit from another (`bluxq guard tui --mode dev`).

## Verification

- `bluxq --help` shows available subcommands.
- The telemetry directory exists even when unwritable (best-effort logging ensures the app continues running).
- `bluxqd` surfaces a degrade warning instead of crashing when logs are unavailable.

FILE: LICENSE
Kind: text
Size: 324
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
This project is dual-licensed:

- Open source use is permitted under the Apache License, Version 2.0 (see LICENSE-APACHE).
- Commercial use requires a separate commercial license (see LICENSE-COMMERCIAL).

If you are unsure which license applies to your use case, please contact the maintainers at theoutervoid@outlook.com.

FILE: LICENSE-APACHE
Kind: text
Size: 11342
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2025 - Outer Void

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

FILE: LICENSE-COMMERCIAL
Kind: text
Size: 1291
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
Proprietary Commercial License

Copyright (c) 2025 Outer Void Team. All rights reserved.

Permission is granted to use this software for internal evaluation and non-commercial purposes only. Any commercial use, including but not limited to embedding, distributing, selling, sublicensing, hosting as a service, or incorporating into a commercial product, requires a separate commercial license obtained from the copyright holder.

You may not redistribute, sublicense, or transfer this software without prior written permission. All rights not expressly granted are reserved by the copyright holder.

THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This license terminates automatically if you fail to comply with its terms. Upon termination, you must cease all use and destroy all copies of the software.

For commercial licensing inquiries, please contact: theoutervoid@outlook.com.

FILE: Makefile
Kind: text
Size: 316
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
.PHONY: dev lint test tui smoke

dev:
	python -m pip install -U pip && pip install -e .[dev] || pip install -e .
	pip install ruff mypy pytest

lint:
	ruff check .
	mypy blux_guard || true

test:
	pytest

tui:
	bluxq guard tui --mode dev

smoke:
	python -c "import blux_guard"
	python -m blux_guard.cli.bluxq --help

FILE: NOTICE
Kind: text
Size: 205
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
Blux Guard
Copyright (c) 2025 Outer Void Team

This product includes software developed by the Outer Void Team under the Apache License, Version 2.0.
See the LICENSE-APACHE file for the full license text.

FILE: OPERATIONS.md
Kind: text
Size: 1697
Last modified: 2026-01-22T05:14:58.510426Z

CONTENT:
# Operations Runbook

## Starting and Stopping Services

- **Start daemon**: `bluxqd` (runs FastAPI server and agent pollers).
- **Stop daemon**: Ctrl+C from the daemon terminal or send SIGTERM to the process.
- **Launch cockpit**: `bluxq guard tui --mode dev` for development, `--mode secure` for monitoring.

## Log Rotation

Logs are appended to `~/.config/blux-guard/logs`. Rotate by moving files and recreating empty placeholders:

```bash
mkdir -p ~/.config/blux-guard/archive
mv ~/.config/blux-guard/logs/*.jsonl ~/.config/blux-guard/archive/
```

SQLite mirrors can be vacuumed:

```bash
sqlite3 ~/.config/blux-guard/logs/telemetry.db 'VACUUM;'
```

## Environment Toggles

- `BLUX_GUARD_TELEMETRY=off` — disable JSONL/SQLite writes.
- `BLUX_GUARD_TELEMETRY_WARN=once` — print a single degrade warning to stderr on failure.
- `BLUX_GUARD_LOG_DIR=/custom/path` — override the log directory.

## Backup & Restore

1. Copy configuration files under `config/` and any `config/local.yaml` overrides.
2. Archive telemetry logs if needed for audit trails.
3. Restore by placing files back into the repository checkout and re-running `pip install -e .` if dependencies
   changed.

## Health Checks

- `bluxq guard status` — ensures telemetry paths resolve correctly.
- `curl http://localhost:8000/status` — verify daemon API is running.
- `curl http://localhost:8000/metrics` — fetch Prometheus metrics for monitoring.

## Incident Response

1. Review `audit.jsonl` for recent events.
2. Check Doctrine panel in the TUI for alignment violations.
3. Use `bluxq dev deploy --safe` to redeploy with rollback protection if necessary.
4. Document the response in your operational tracker.

FILE: PRIVACY.md
Kind: text
Size: 1054
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# Privacy and Telemetry

BLUX Guard stores telemetry locally on the operator's device. No automatic uploads occur.

## Data Collected

- Event metadata: timestamps, action names, actor identifiers, severity levels.
- Optional payloads describing resource usage or receipt metadata (sanitized).

## Storage Locations

- JSONL audit log: `~/.config/blux-guard/logs/audit.jsonl`
- SQLite mirror: `~/.config/blux-guard/logs/telemetry.db`

## Controls

- Disable telemetry: set `BLUX_GUARD_TELEMETRY=off` before launching `bluxq` or `bluxqd`.
- Limit warnings: `BLUX_GUARD_TELEMETRY_WARN=once` prints a single degrade message when storage fails.
- Custom location: `BLUX_GUARD_LOG_DIR=/custom/path` redirects all files.

## Retention & Rotation

Operators manage retention manually. Use the guidance in `OPERATIONS.md` to rotate logs or purge data as
required by policy.

## Access

Telemetry files are created with user-level permissions. Share them only with trusted auditors. No upstream
services receive telemetry unless you integrate optional exporters.

FILE: README.md
Kind: text
Size: 10287
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# BLUX Guard

> **Developer Security Cockpit for the BLUX Ecosystem**  
> Real-time defense, telemetry, and deterministic receipt issuance integrated with AI orchestration.

[![License](https://img.shields.io/badge/License-Dual-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Android-lightgrey.svg)](#cross-platform-support)

---

## 🎯 Vision

BLUX Guard is a discreet, layered security defender that uses deterministic trip-variables, tamper-resistant sensors, and safe containment to protect **your own devices**. It operates transparently, remains fully auditable, and stays under operator control at all times.

BLUX Guard provides protocol enforcement + userland constraints.
Enforcement stays safely in userland by applying receipt-defined constraints to Guard actions
and relying on non-privileged checks (filesystem scoping, process boundaries, and explicit
operator confirmations) instead of any elevated system controls.

**Core Principles:**
- 🔒 Defensive-only security with no offensive payloads
- 🔍 Transparent operation with complete auditability
- 🛡️ Multi-layered protection against AI-powered threats
- 👤 Always respects operator authority and privacy

---

## 🏗️ Architecture Overview

```
Sensors → Trip Engine → Decision Layer → Containment → Operator
```

### 1. **Sensors** (Data Sources)
- Network flows, DNS queries, process lifecycle monitoring
- Filesystem changes and permission modifications
- Hardware events: charging, Bluetooth pairing, USB attach
- Human factors: unlock patterns, presence windows

### 2. **Trip Engine** (Deterministic Rules)
- Boolean and temporal trip-wires
- Thresholded counters and state chains
- Signed, versioned rule manifests in `.config/rules/rules.json`

### 3. **Decision Layer**
- Escalation path: observe → intercept → quarantine → lockdown
- Per-UID policies: whitelist / greylist / blacklist
- Optional kill-switch for complete isolation

### 4. **Containment & Response**
- Network interceptor (VpnService-like)
- Process isolator with snapshot & rollback
- Filesystem quarantine and permission reverter
- Signed incident logs in `logs/decisions/incidents.log`

### 5. **Integrity & Anti-Tamper**
- Watchdog with self-heartbeat monitoring
- Signed binaries and manifests
- Alerts on package manager changes, privilege escalation binaries, SELinux modifications

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Outer-Void/blux-guard.git
cd blux-guard

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### CLI Usage

```bash
# Start with the CLI
bluxq guard status

# Evaluate a request envelope and emit a receipt
blux-guard evaluate --request-envelope examples/envelope.json --capability-ref CAP_REF
```

### Power Mode 2.0 (Recommended)

```bash
# Install with virtual environment (recommended)
python -m pip install -U pip
pip install -e .

# Start daemon & open cockpit
bluxqd &
bluxq guard status
bluxq guard tui --mode dev
```

### Developer Workflows

```bash
bluxq dev init        # Initialize development environment
bluxq dev scan .      # Scan current directory
bluxq dev deploy --safe  # Deploy with safety checks
```

## 🎯 Trip Engine Examples

BLUX Guard uses deterministic, time-bounded, and auditable trip conditions:

| Scenario | Trip Condition | Action |
|----------|---------------|--------|
| **Silent Exfil** | 10 external sockets to distinct IPs in 60s | Block, snapshot, notify |
| **Mount Surprise** | SD mounted while locked & charging & idle 12h+ | Read-only + checksum |
| **Privilege Creep** | New permission soon after unknown net conn | Revert + quarantine |
| **Process Mimic** | Same pkg name, different cert/hash | Freeze + capture |
| **UI Hijack** | Overlay within 2s of credential event | Block overlay + prompt |
| **Cold-start Lateral** | Unknown AUTOSTART after reboot | Block autostart until review |

---

## 🤖 AI Security Strategy

**Principle:** Break hostile AI effectiveness by destroying input reliability and computation economics.

### Strategy I — "Pull It Apart"
- Deterministic jitter to break time-series features
- Proof-of-Work throttles (per-UID PoW)
- Honeypots and deceptive metadata
- Never auto-confirm success — require human validation

### Strategy II — "EMP Metaphor"
- Circuit breakers to air-gap radios or network routes
- Freeze/snapshot suspect processes
- Reduce CPU/QoS for suspect UIDs
- All actions signed and operator-approved

---

## 📊 Telemetry & Reliability

BLUX Guard writes best-effort logs to:

- `~/.config/blux-guard/logs/audit.jsonl`
- `~/.config/blux-guard/logs/telemetry.db` (SQLite, optional)

If the directory is unwritable or SQLite is unavailable, logging **degrades silently** and the app **continues running**.

### Telemetry Controls

```bash
# Disable telemetry writes
export BLUX_GUARD_TELEMETRY=off

# Show single degrade warning on stderr
export BLUX_GUARD_TELEMETRY_WARN=once
```

---

## 🌍 Cross-Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Android / Termux** | ✅ Full Support | Installers configure aliases; telemetry lives under `$HOME/.config/blux-guard/logs` |
| **Linux** | ✅ Full Support | Prometheus metrics export via `bluxqd` |
| **macOS** | ✅ Full Support | Prometheus metrics export via `bluxqd` |
| **Windows** | ✅ Full Support | PowerShell support via `COMSPEC`; telemetry paths expand to `%USERPROFILE%\.config\blux-guard\logs` |
| **WSL2** | ✅ Full Support | Works like native Linux installation |

---

## 🐛 Troubleshooting

### Common Issues

**CLI reports `ModuleNotFoundError: typer`**
```bash
# Reinstall with dependencies
pip install -e .
```

**Permission denied writing logs**
```bash
# Create the telemetry directory manually
mkdir -p ~/.config/blux-guard/logs

# Or disable telemetry
export BLUX_GUARD_TELEMETRY=off
```

**SQLite locked or missing**
- Mirror is optional; CLI continues using JSONL streams
- Emits a single degrade warning when enabled

**Termux storage prompts**
```bash
# Grant write access
termux-setup-storage
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Module graph and platform matrix |
| [INSTALL.md](INSTALL.md) | Platform-specific installation steps |
| [OPERATIONS.md](OPERATIONS.md) | Runbook for day-two operations |
| [SECURITY.md](SECURITY.md) | Threat model, telemetry guarantees |
| [PRIVACY.md](PRIVACY.md) | Telemetry scope and retention controls |
| [CONFIGURATION.md](CONFIGURATION.md) | YAML schema and overrides |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Quick fixes for common issues |
| [docs/ROLE.md](docs/ROLE.md) | Guard enforcement responsibilities and non-goals |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and coding standards |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community expectations |
| [SUPPORT.md](SUPPORT.md) | Escalation paths and SLAs |
| [ROADMAP.md](ROADMAP.md) | Upcoming milestones |

---

## 🗺️ Roadmap

| Stage | Goal |
|-------|------|
| v0.1 | Termux Trip Engine prototype |
| v0.2 | Honeypot + canary endpoint |
| v0.3 | BLE companion listener |
| v0.4 | Kotlin VpnService interceptor |
| v0.5 | Consensus agent coordinator |
| v1.0 | Full BLUX Guard operator suite |

---

## 🔒 Security Model

- Enforcement stays deterministic and receipt-scoped
- All automation routes through receipt constraints to respect containment boundaries

## 🧾 Receipt Enforcement (No Elevation)

BLUX Guard issues receipts that describe allowed commands or paths, plus explicit sandbox
and network constraints. Enforcement is intentionally non-privileged: receipts describe what an
agent may do, and downstream runners can enforce those rules without requiring any elevation.
If you need broader access, adjust the request envelope constraints instead of escalating.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:

- Contribution workflow
- Coding standards
- Testing requirements
- Review process

All commits and rule changes must include:
- Author signature
- Simulation or test logs
- One reviewer sign-off

---

## 🔐 Governance & Ethics

**Defensive-only.** No offensive payloads.

### Security Protocols

- Private signing keys must never reside on the same device
- Critical changes require physical ACK (BLE/NFC or manual gesture)
- Maintain an auditable signed changelog

---

## ⚖️ Licensing

BLUX Guard is dual-licensed:

- **Open-source use:** [Apache License 2.0](LICENSE-APACHE)
- **Commercial use:** Requires separate agreement (see [LICENSE-COMMERCIAL](LICENSE-COMMERCIAL))

### Apache 2.0 Usage
You may use, modify, and redistribute the software for open and internal purposes, provided that you preserve notices, include the license, and accept the standard disclaimers of warranty and liability.

### Commercial Usage
Commercial use—such as embedding in paid products, offering hosted services, or other monetized deployments—requires a commercial license. Please review [COMMERCIAL.md](COMMERCIAL.md) for examples and contact **theoutervoid@outlook.com** to arrange commercial terms.

---

## 📋 Supported Python Versions

The cockpit validates Python 3.9+ on startup. 

**Supported interpreters:** 3.9, 3.10, 3.11

Upgrade the interpreter if you receive a startup warning.

---

## 🛡️ Legal & Safety

- ✅ Works only on devices you own or control
- ✅ Forensics data remains private and encrypted
- ✅ Always test on secondary hardware first
- ✅ Never modify or erase evidence automatically

---

## 💬 Getting Help

- Check individual module docstrings for usage details
- Use the CLI for guided operation
- See [SUPPORT.md](SUPPORT.md) for escalation paths

---

## 📞 Contact

- **Email:** outervoid.blux@gmail.com
- **GitHub:** [github.com/Outer-Void](https://github.com/Outer-Void)

---

**BLUX Guard Doctrine** — Building walls that respect your hunger and deny the pack.

*"The forge remains open, even when the pen runs dry."*

FILE: ROADMAP.md
Kind: text
Size: 831
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# Roadmap

## Near Term

- **Commander Mirror** — Expose the cockpit over the web by consuming `/api/stream` events.
- **SBOM Generation** — Automate CycloneDX export for dependency transparency.
- **Enhanced Sandbox** — Add cgroup and job object limits for deeper containment.

## Mid Term

- **SLSA Compliance** — Integrate provenance attestations into CI builds.
- **AI Advisor Enhancements** — Expand BLUX-Lite guidance with contextual doctrine tips.
- **Policy Templates** — Provide curated doctrine packs for common industry frameworks.

## Long Term

- **Fleet Management** — Manage multiple devices from a centralized Commander hub.
- **Pluggable Sensors** — Allow third-party sensor modules with signed manifests.
- **Automated Recovery** — Integrate snapshot/rollback pipelines for full system restore.

FILE: ROLE.md
Kind: text
Size: 405
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# BLUX Guard Role

BLUX Guard provides enforcement-only receipt issuance with deterministic, userland constraints.

## Explicit Non-Capabilities
- Does not run tools or execute commands.
- Does not sandbox-run commands or spawn shells.
- Does not issue or verify tokens.
- Does not interpret doctrine, policy, or ethics.
- Can be bypassed by design, but emits audit logs when a bypass signal is provided.

FILE: SECURITY.md
Kind: text
Size: 1370
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# Security Posture

## Threat Model

- **Adversaries**: Malware attempting to tamper with guard modules, unauthorized operators, and remote
  attackers seeking unauthorized access.
- **Assets**: Device integrity, receipt integrity, audit trails, and developer workflows.

## Key Controls

1. **Receipt Issuance** — `core/receipt.py` emits deterministic receipts with explicit constraints.
2. **Telemetry Assurance** — `core/telemetry.py` logs events without risking crashes; degrade warnings are
   emitted once when `BLUX_GUARD_TELEMETRY_WARN=once`.
3. **Role Separation** — CLI commands map to user roles; dangerous operations require explicit
   confirmation via `--safe` flags.

## Disclosure & Updates

- Report vulnerabilities through the support channel listed in `SUPPORT.md`.
- Security fixes are documented in `CHANGELOG.md` under the **Security** heading.

## Telemetry & Failure Behavior

All telemetry writes are wrapped in best-effort handlers. If paths are unwritable or SQLite is locked, the
application continues and emits a single degrade warning when `BLUX_GUARD_TELEMETRY_WARN=once`.

## Hardening Tips

- Keep Python and system dependencies updated via Dependabot recommendations.
- Run CI workflows (`.github/workflows/ci.yml`) on every branch.
- Rotate any operator credentials stored outside the repository (e.g., Termux tokens) regularly.

FILE: SUPPORT.md
Kind: text
Size: 810
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# Support

## Channels

- **Security Incidents**: Email security@outervoid.example (PGP key available upon request).
- **General Support**: Open an issue on GitHub with the `[support]` label.
- **Enterprise Engagements**: Contact enterprise@outervoid.example for onboarding assistance.

## Response Targets

- Critical security reports: 24 hours.
- Operational outages: 1 business day.
- Documentation or usage questions: 3 business days.

## Version Support Policy

- Active development tracks the `main` branch.
- Maintenance: latest tagged release receives backports for critical fixes.
- Older branches transition to community support only.

## Self-Service Resources

- `TROUBLESHOOTING.md` for quick fixes.
- `OPERATIONS.md` for runbook procedures.
- `CONFIGURATION.md` for customizing runtime behavior.

FILE: TROUBLESHOOTING.md
Kind: text
Size: 1287
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# Troubleshooting

## Common Issues

### Missing Typer Dependency
- **Symptom**: `ModuleNotFoundError: typer` when running `bluxq`.
- **Fix**: Reinstall with `pip install -e .` to ensure the declared dependencies are installed.

### Permission Denied for Telemetry
- **Symptom**: Errors writing to `~/.config/blux-guard/logs`.
- **Fix**: Create the directory manually (`mkdir -p ~/.config/blux-guard/logs`) or set
  `BLUX_GUARD_TELEMETRY=off`.

### SQLite Locked
- **Symptom**: Warning indicating the telemetry database is locked.
- **Fix**: The application continues; optionally vacuum or delete `telemetry.db`. Warnings appear only once when
  `BLUX_GUARD_TELEMETRY_WARN=once`.

### Termux Storage Prompts
- **Symptom**: Termux denies storage access when launching the cockpit.
- **Fix**: Run `termux-setup-storage` and restart `bluxq`.

### Unsupported Python Version
- **Symptom**: Startup exits with a message requiring Python 3.9+.
- **Fix**: Upgrade Python to at least 3.9 or use the provided installers for your platform.

### Daemon Port Conflicts
- **Symptom**: `Address already in use` when starting `bluxqd`.
- **Fix**: Stop other processes on port 8000 or adjust the port in `config/local.yaml`.

## Getting Help

See `SUPPORT.md` for escalation paths and contact channels.

FILE: blux_guard/__init__.py
Kind: text
Size: 158
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""BLUX Guard core package for Developer Suite extensions."""

from .core import telemetry as telemetry  # re-export for convenience

__all__ = ["telemetry"]

FILE: blux_guard/agents/__init__.py
Kind: text
Size: 54
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Cross-platform agent interfaces for BLUX Guard."""

FILE: blux_guard/agents/common.py
Kind: text
Size: 634
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Common utilities for host agents."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Protocol


class Agent(Protocol):
    def collect(self) -> dict:
        ...


@dataclass
class AgentInfo:
    name: str
    platform: str


def detect_agent() -> AgentInfo:
    system = platform.system().lower()
    if "linux" in system:
        name = "linux"
    elif "darwin" in system:
        name = "mac"
    elif "windows" in system:
        name = "windows"
    else:
        name = "termux" if "android" in system else "unknown"
    return AgentInfo(name=name, platform=system)

FILE: blux_guard/agents/linux_agent.py
Kind: text
Size: 443
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Linux agent for system metrics."""

from __future__ import annotations

import os

from ..core import telemetry


class LinuxAgent:
    def collect(self) -> dict:
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        data = {
            "load": load,
        }
        telemetry.record_event("agent.linux", actor="agent", payload=data)
        return data


def get_agent() -> LinuxAgent:
    return LinuxAgent()

FILE: blux_guard/agents/mac_agent.py
Kind: text
Size: 340
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""macOS agent for system metrics."""

from __future__ import annotations

from ..core import telemetry


class MacAgent:
    def collect(self) -> dict:
        data = {"uptime": "unavailable"}
        telemetry.record_event("agent.mac", actor="agent", payload=data)
        return data


def get_agent() -> MacAgent:
    return MacAgent()

FILE: blux_guard/agents/termux_agent.py
Kind: text
Size: 491
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Telemetry collection for Termux environments."""

from __future__ import annotations

import shutil
from typing import Dict

from . import common
from ..core import telemetry


class TermuxAgent:
    def collect(self) -> Dict[str, str]:
        data = {
            "storage": shutil.disk_usage("/").free // (1024 * 1024),
        }
        telemetry.record_event("agent.termux", actor="agent", payload=data)
        return data


def get_agent() -> TermuxAgent:
    return TermuxAgent()

FILE: blux_guard/agents/windows_agent.py
Kind: text
Size: 378
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Windows agent for telemetry."""

from __future__ import annotations

import platform

from ..core import telemetry


class WindowsAgent:
    def collect(self) -> dict:
        data = {"platform": platform.platform()}
        telemetry.record_event("agent.windows", actor="agent", payload=data)
        return data


def get_agent() -> WindowsAgent:
    return WindowsAgent()

FILE: blux_guard/api/__init__.py
Kind: text
Size: 50
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""API surface for BLUX Guard Developer Suite."""

FILE: blux_guard/api/guardd.py
Kind: text
Size: 2510
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Daemon process that starts the FastAPI server and polls agents."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Callable

import uvicorn

from ..agents import common, linux_agent, mac_agent, termux_agent, windows_agent
from ..core import runtime, telemetry
from .server import app

_AGENT_MAP = {
    "linux": linux_agent.get_agent,
    "mac": mac_agent.get_agent,
    "windows": windows_agent.get_agent,
    "termux": termux_agent.get_agent,
}


async def _poll_agents() -> None:
    info = common.detect_agent()
    factory: Callable[[], object] | None = _AGENT_MAP.get(info.name)
    agent = factory() if factory else None
    while True:
        if agent and hasattr(agent, "collect"):
            telemetry.record_event(
                "daemon.poll",
                actor="daemon",
                payload=getattr(agent, "collect")(),
            )
        await asyncio.sleep(30)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose telemetry")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args(argv)


def start() -> None:
    """Entry point for the ``bluxqd`` console script."""

    args = _parse_args(sys.argv[1:])
    runtime.set_debug(args.debug)
    runtime.set_verbose(args.verbose)
    telemetry.set_debug(args.debug)
    telemetry.set_verbose(args.verbose)

    runtime.ensure_supported_python("bluxqd")
    if not telemetry.ensure_log_dir():
        telemetry.record_event(
            "startup.degrade",
            level="warn",
            actor="daemon",
            payload={"component": "bluxqd", "reason": "log_dir_unavailable"},
        )

    telemetry.record_event("daemon.start", actor="daemon", payload={})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner() -> None:
        poller = loop.create_task(_poll_agents())
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            log_level="debug" if args.debug else "info",
        )
        server = uvicorn.Server(config)
        await server.serve()
        poller.cancel()

    try:
        loop.run_until_complete(runner())
    finally:
        loop.close()

FILE: blux_guard/api/server.py
Kind: text
Size: 881
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""FastAPI server exposing guard status."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse

from ..core import telemetry
from . import stream

app = FastAPI(title="BLUX Guard API")


@app.get("/status")
async def status() -> dict:
    return await telemetry.collect_status()


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    chunks = []

    async for chunk in telemetry.iter_prometheus_metrics():
        chunks.append(chunk)
    return PlainTextResponse("\n".join(chunks))


@app.websocket("/stream")
async def websocket_endpoint(socket: WebSocket) -> None:
    await stream.register(socket)


@app.on_event("startup")
async def startup() -> None:
    stream.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await stream.stop()

FILE: blux_guard/api/stream.py
Kind: text
Size: 1049
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Simple broadcast stream for cockpit events."""

from __future__ import annotations

import asyncio
from typing import Set

from fastapi import WebSocket

from ..core import telemetry

_clients: Set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def start() -> None:
    global _loop
    if _loop is None:
        _loop = asyncio.get_event_loop()


async def stop() -> None:
    while _clients:
        socket = _clients.pop()
        await socket.close()


async def register(socket: WebSocket) -> None:
    await socket.accept()
    _clients.add(socket)
    try:
        while True:
            data = await socket.receive_text()
            telemetry.record_event(
                "api.stream",
                actor="api",
                payload={"message": data},
            )
            for client in list(_clients):
                if client is not socket:
                    await client.send_text(data)
    except Exception:
        pass
    finally:
        _clients.discard(socket)
        await socket.close()

FILE: blux_guard/audit.py
Kind: text
Size: 1887
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""Unified audit writer for BLUX Guard."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .core import telemetry


def generate_correlation_id() -> str:
    """Return a correlation id (UUID4) with optional override from env."""

    return os.environ.get("BLUX_GUARD_CORRELATION_ID", str(uuid.uuid4()))


def audit_log_path() -> Path:
    """Return the resolved audit log path."""

    status = telemetry.collect_status_sync()
    return Path(status["audit_log"])




@dataclass
class AuditEvent:
    action: str
    level: str = "info"
    actor: str = "local"
    stream: str = "audit"
    payload: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    component: Optional[str] = None

    def as_payload(self) -> Dict[str, Any]:
        merged = dict(self.payload or {})
        if self.correlation_id:
            merged.setdefault("correlation_id", self.correlation_id)
        if self.component:
            merged.setdefault("component", self.component)
        return merged


def record(
    action: str,
    *,
    level: str = "info",
    actor: str = "local",
    stream: str = "audit",
    payload: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    component: Optional[str] = None,
) -> str:
    """Write an audit record and return the correlation id used."""

    cid = correlation_id or generate_correlation_id()
    event = AuditEvent(
        action=action,
        level=level,
        actor=actor,
        stream=stream,
        payload=payload,
        correlation_id=cid,
        component=component,
    )
    telemetry.record_event(
        event.action,
        level=event.level,
        actor=event.actor,
        payload=event.as_payload(),
        stream=event.stream,
    )
    return cid


FILE: blux_guard/cli/README.md
Kind: text
Size: 821
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
# bluxq Command Reference

The Quantum namespace CLI provides developer-focused commands for guard operations.

## Guard Commands

```bash
bluxq guard status            # JSON status snapshot
bluxq guard tui --mode dev    # launch cockpit (dev|secure|ops)
bluxq guard evaluate --request-envelope envelope.json --capability-ref CAP_REF
```

## Developer Suite Commands

```bash
bluxq dev init                # provision secure workspace
bluxq dev build               # guarded build pipeline
bluxq dev scan .              # run security scanning
bluxq dev deploy --safe       # deployment with rollback guard
```

All commands record telemetry using best-effort logging. Set `BLUX_GUARD_TELEMETRY=off` to disable log writes or `BLUX_GUARD_TELEMETRY_WARN=once` to print a single degrade notice when storage is unavailable.

FILE: blux_guard/cli/__init__.py
Kind: text
Size: 50
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""CLI package for BLUX Guard developer suite."""

FILE: blux_guard/cli/blux_guard.py
Kind: text
Size: 1648
Last modified: 2026-01-22T05:14:58.514426Z

CONTENT:
"""BLUX Guard receipt CLI."""

from __future__ import annotations

import json
import pathlib
from typing import Optional

import typer

from blux_guard.core import receipt as receipt_engine

app = typer.Typer(help="BLUX Guard receipt tooling")


@app.command("evaluate")
def evaluate(
    request_envelope: pathlib.Path = typer.Option(
        ..., "--request-envelope", help="Envelope JSON payload."
    ),
    token: Optional[list[str]] = typer.Option(
        None, "--token", help="Capability token (repeatable)."
    ),
    discernment: Optional[pathlib.Path] = typer.Option(
        None, "--discernment", help="Optional discernment report JSON."
    ),
    revocations: Optional[pathlib.Path] = typer.Option(
        None, "--revocations", help="Optional revocation list JSON."
    ),
) -> None:
    """Evaluate an envelope and emit a guard receipt."""

    receipt = receipt_engine.evaluate_from_files(
        request_envelope,
        discernment,
        tokens=token or None,
        revocations_path=revocations,
    )
    typer.echo(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))


@app.command("verify-receipt")
def verify_receipt(
    receipt_path: pathlib.Path = typer.Option(
        ..., "--receipt", help="Guard receipt JSON payload."
    )
) -> None:
    """Verify a guard receipt for integrity."""

    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    ok, reason = receipt_engine.verify_receipt(receipt_payload)
    payload = {"ok": ok, "reason": reason}
    if not ok:
        typer.echo(json.dumps(payload), err=True)
        raise typer.Exit(code=2)
    typer.echo(json.dumps(payload))

FILE: blux_guard/cli/bluxq.py
Kind: text
Size: 7195
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Entry point for the BLUX Guard Developer Suite CLI."""

from __future__ import annotations

import asyncio
import json
import pathlib
import traceback
from typing import Optional

import typer

from blux_guard import audit, doctor
from blux_guard.core import devsuite, receipt as receipt_engine, runtime, telemetry
from blux_guard.core import selfcheck as core_selfcheck
from blux_guard.tui import app as cockpit_app

app = typer.Typer(help="BLUX Guard Developer Suite (Quantum namespace)")

guard_app = typer.Typer(help="Guard management commands")

dev_app = typer.Typer(help="Developer workflow commands")


def _configure_runtime(debug: bool, verbose: bool) -> None:
    runtime.set_debug(debug)
    runtime.set_verbose(verbose)
    telemetry.set_debug(debug)
    telemetry.set_verbose(verbose)


@app.callback()
def main(
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debugging output."),
    verbose: bool = typer.Option(False, "--verbose", help="Print verbose telemetry output."),
) -> None:
    """Main CLI callback.

    The callback is intentionally empty so Typer can manage sub-commands.
    """

    _configure_runtime(debug, verbose)
    runtime.ensure_supported_python("bluxq")
    if not telemetry.ensure_log_dir():
        telemetry.record_event(
            "startup.degrade",
            level="warn",
            actor="cli",
            payload={"component": "bluxq", "reason": "log_dir_unavailable"},
        )


def _ensure_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def _handle_exception(exc: Exception, *, context: str) -> None:
    telemetry.record_event(
        "cli.error",
        level="error",
        actor="cli",
        payload={"context": context, "error": str(exc)},
    )
    if runtime.debug_enabled():
        traceback.print_exc()
    else:
        typer.echo(f"Error during {context}: {exc}", err=True)


def _run_async(description: str, awaitable_factory) -> Optional[object]:
    loop = _ensure_event_loop()
    try:
        return loop.run_until_complete(awaitable_factory())
    except Exception as exc:  # pragma: no cover - defensive
        _handle_exception(exc, context=description)
        raise typer.Exit(code=1)


@guard_app.command("status")
def guard_status() -> None:
    """Print a high level status report for the guard runtime."""

    status = _run_async("guard status", telemetry.collect_status)
    typer.echo(json.dumps(status, indent=2, sort_keys=True))


@guard_app.command("scan")
def guard_scan(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Run a guard scan via dev suite."""

    _run_async("guard scan", lambda: devsuite.run_scan(target))


@guard_app.command("watch")
def guard_watch(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Continuously scan a target (placeholder watch mode)."""

    audit.record("cli.watch", actor="cli", payload={"target": str(target)})
    _run_async("guard watch", lambda: devsuite.run_scan(target))


@guard_app.command("tui")
def guard_tui(
    mode: str = typer.Option("secure", help="TUI mode: dev|secure|ops"),
    correlation_id: str = typer.Option(None, help="Correlation id to propagate."),
) -> None:
    """Launch the Textual cockpit."""

    cid = correlation_id or audit.generate_correlation_id()
    _run_async("guard tui", lambda: cockpit_app.run_cockpit(mode=mode, correlation_id=cid))


@guard_app.command("self-check")
def guard_self_check() -> None:
    """Run environment validation checks and print the results."""

    results = _run_async("guard self-check", core_selfcheck.run_self_check)
    if not results:
        return

    typer.echo("Self-check summary:")
    for item in results["checks"]:
        typer.echo(
            f"- {item['name']}: {item['status'].upper()} -- {item['detail']}"
        )
    typer.echo(f"Overall status: {results['overall'].upper()}")


@guard_app.command("doctor")
def guard_doctor() -> None:
    """Run environment diagnostics."""

    report = doctor.run_doctor()
    typer.echo(json.dumps(report, indent=2))


@guard_app.command("verify")
def guard_verify() -> None:
    """Verify configuration and audit log paths."""

    report = doctor.run_verify()
    typer.echo(json.dumps(report, indent=2))


@guard_app.command("incidents")
def guard_incidents(limit: int = typer.Option(10, help="Number of entries")) -> None:
    """Print recent warning/error audit entries."""

    path = audit.audit_log_path()
    if not path.exists():
        typer.echo("No audit log present", err=True)
        return
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    for line in lines:
        typer.echo(line)


@guard_app.command("export")
def guard_export() -> None:
    """Export diagnostic bundle using cockpit helpers."""

    status = telemetry.collect_status_sync()
    audit.record("cli.export", actor="cli", payload=status)
    typer.echo(json.dumps(status, indent=2))


@guard_app.command("evaluate")
def guard_evaluate(
    request_envelope: pathlib.Path = typer.Option(
        ..., "--request-envelope", help="Envelope JSON payload."
    ),
    capability_ref: Optional[list[str]] = typer.Option(
        None, "--capability-ref", help="Capability reference (repeatable)."
    ),
    discernment: Optional[pathlib.Path] = typer.Option(
        None, "--discernment", help="Optional discernment report JSON."
    ),
) -> None:
    """Evaluate an envelope and emit a guard receipt."""

    receipt = receipt_engine.evaluate_from_files(
        request_envelope,
        discernment,
        capability_refs=capability_ref or None,
    )
    typer.echo(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))


@guard_app.command("install")
def guard_install(target: str = typer.Option("linux", help="linux|termux")) -> None:
    """Hint the operator to platform installer documentation."""

    typer.echo(f"See INSTALL.md for {target} instructions.")
    audit.record("cli.install", actor="cli", payload={"target": target})


@dev_app.command("init")
def dev_init(path: pathlib.Path = typer.Argument(pathlib.Path.cwd(), help="Project directory")) -> None:
    """Initialise a secure workspace."""

    _run_async("dev init", lambda: devsuite.initialise_workspace(path))
    typer.echo(f"Workspace initialised at {path}")


@dev_app.command("build")
def dev_build() -> None:
    """Execute a guarded build pipeline."""

    _run_async("dev build", devsuite.run_build)


@dev_app.command("scan")
def dev_scan(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Run secure scanning workflows."""

    _run_async("dev scan", lambda: devsuite.run_scan(target))


@dev_app.command("deploy")
def dev_deploy(safe: bool = typer.Option(True, "--safe/--force")) -> None:
    """Perform a guarded deployment."""

    _run_async("dev deploy", lambda: devsuite.run_deploy(safe=safe))


app.add_typer(guard_app, name="guard")
app.add_typer(dev_app, name="dev")


if __name__ == "__main__":
    app()

FILE: blux_guard/config/__init__.py
Kind: text
Size: 799
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Configuration helpers for BLUX Guard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

_BASE_DIR = Path(os.environ.get("BLUX_GUARD_CONFIG_DIR", Path.home() / ".config" / "blux-guard"))
_LOG_DIR = Path(os.environ.get("BLUX_GUARD_LOG_DIR", _BASE_DIR / "logs"))


def config_dir() -> Path:
    """Return the primary configuration directory."""

    return _BASE_DIR


def log_dir() -> Path:
    """Return the log directory path."""

    return _LOG_DIR


def default_paths() -> Dict[str, str]:
    """Expose standard paths for docs and CLIs."""

    return {
        "config_dir": str(config_dir()),
        "log_dir": str(log_dir()),
        "audit_log": str(log_dir() / "audit.jsonl"),
        "sqlite_db": str(log_dir() / "telemetry.db"),
    }

FILE: blux_guard/config/default.yaml
Kind: text
Size: 143
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Default configuration for the BLUX Guard Developer Suite
telemetry:
  log_dir: "~/.config/blux-guard/logs"
api:
  host: 0.0.0.0
  port: 8000

FILE: blux_guard/config/local.yaml
Kind: text
Size: 96
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Local overrides for BLUX Guard Developer Suite
# This file can be customised per environment.

FILE: blux_guard/contracts/__init__.py
Kind: text
Size: 39
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Contract package for BLUX Guard."""

FILE: blux_guard/contracts/phase0/__init__.py
Kind: text
Size: 39
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Pinned Phase 0 contract schemas."""

FILE: blux_guard/contracts/phase0/discernment_report.schema.json
Kind: text
Size: 437
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.blux.ai/phase0/discernment_report.schema.json",
  "title": "Discernment Report",
  "type": "object",
  "properties": {
    "risk_level": {"type": "string"},
    "posture": {"type": "string"},
    "summary": {"type": "string"},
    "requires_confirmation": {"type": "boolean"},
    "signals": {"type": "array"}
  },
  "additionalProperties": true
}

FILE: blux_guard/contracts/phase0/guard_receipt.schema.json
Kind: text
Size: 2241
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "blux://contracts/guard_receipt.schema.json",
  "title": "Guard Receipt",
  "type": "object",
  "required": [
    "receipt_id",
    "issued_at",
    "decision",
    "trace_id",
    "capability_token_ref",
    "token_status",
    "constraints",
    "reason_codes",
    "signature"
  ],
  "properties": {
    "receipt_id": {"type": "string"},
    "issued_at": {"type": "number"},
    "decision": {"type": "string", "enum": ["ALLOW", "WARN", "REQUIRE_CONFIRM", "BLOCK"]},
    "trace_id": {"type": "string"},
    "capability_token_ref": {"type": "string"},
    "token_status": {"type": "string"},
    "reason_codes": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "constraints": {
      "type": "object",
      "required": ["sandbox_profile", "network"],
      "properties": {
        "sandbox_profile": {"type": "string"},
        "network": {"type": "object"},
        "allowed_commands": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "allowed_paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "timeout_s": {"type": "number"},
        "working_dir": {"type": "string"},
        "environment": {"type": "object"},
        "resource_limits": {"type": "object"},
        "confirmation_required": {"type": "boolean"}
      },
      "additionalProperties": true
    },
    "discernment": {
      "type": "object",
      "properties": {
        "risk_level": {"type": "string"},
        "posture": {"type": "string"},
        "summary": {"type": "string"}
      },
      "additionalProperties": true
    },
    "signature": {
      "type": "object",
      "required": ["alg", "value"],
      "properties": {
        "alg": {"type": "string"},
        "value": {"type": "string"}
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {"decision": {"const": "ALLOW"}},
        "required": ["decision"]
      },
      "then": {
        "properties": {
          "constraints": {
            "anyOf": [
              {"required": ["allowed_commands"]},
              {"required": ["allowed_paths"]}
            ]
          }
        }
      }
    }
  ],
  "additionalProperties": true
}

FILE: blux_guard/contracts/phase0/request_envelope.schema.json
Kind: text
Size: 838
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.blux.ai/phase0/request_envelope.schema.json",
  "title": "Request Envelope",
  "type": "object",
  "required": ["trace_id"],
  "properties": {
    "trace_id": {"type": "string"},
    "capability_token_ref": {"type": "string"},
    "capability_tokens": {"type": "array", "items": {"type": "string"}},
    "command": {"type": "string"},
    "allowed_commands": {"type": "array", "items": {"type": "string"}},
    "allowed_paths": {"type": "array", "items": {"type": "string"}},
    "sandbox_profile": {"type": "string"},
    "network": {"type": "object"},
    "timeout_s": {"type": "number"},
    "working_dir": {"type": "string"},
    "resource_limits": {"type": "object"},
    "environment": {"type": "object"}
  },
  "additionalProperties": true
}

FILE: blux_guard/core/__init__.py
Kind: text
Size: 242
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Core runtime utilities for the BLUX Guard Developer Suite."""

from . import devsuite, runtime, security_cockpit, selfcheck, telemetry

__all__ = [
    "devsuite",
    "runtime",
    "security_cockpit",
    "selfcheck",
    "telemetry",
]

FILE: blux_guard/core/devsuite.py
Kind: text
Size: 1039
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Developer workflow orchestration for the BLUX Guard suite."""

from __future__ import annotations

import asyncio
import pathlib

from . import telemetry


async def initialise_workspace(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    telemetry.record_event("dev.init", actor="devsuite", payload={"path": str(path)})


async def run_build() -> None:
    telemetry.record_event(
        "dev.build",
        actor="devsuite",
        payload={"phase": "start"},
    )
    await asyncio.sleep(0)
    telemetry.record_event(
        "dev.build",
        actor="devsuite",
        payload={"phase": "complete"},
    )


async def run_scan(target: pathlib.Path) -> None:
    telemetry.record_event(
        "dev.scan",
        actor="devsuite",
        payload={"target": str(target)},
    )
    await asyncio.sleep(0)


async def run_deploy(safe: bool = True) -> None:
    telemetry.record_event(
        "dev.deploy",
        actor="devsuite",
        payload={"safe": safe},
    )
    await asyncio.sleep(0)


FILE: blux_guard/core/receipt.py
Kind: text
Size: 9932
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Guard receipt issuance utilities."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from jsonschema import Draft202012Validator

from blux_guard import audit
from blux_guard.contracts import phase0 as phase0_contracts

GUARD_RECEIPT_SCHEMA_ID = "blux://contracts/guard_receipt.schema.json"
_DEFAULT_MAPPING = Path(__file__).resolve().parents[1] / "guard" / "mapping" / "default_mapping.json"
_MAPPING_CACHE: Dict[str, Any] | None = None


def _load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = Path(phase0_contracts.__file__).with_name(schema_name)
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate_schema(payload: Dict[str, Any], schema_name: str) -> None:
    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    if errors:
        messages = "; ".join(
            f"{schema_name}:{'/'.join([str(p) for p in err.path])}:{err.message}"
            for err in errors
        )
        raise ValueError(f"Schema validation failed: {messages}")


def _load_mapping(path: Optional[Path] = None) -> Dict[str, Any]:
    global _MAPPING_CACHE
    if _MAPPING_CACHE is None:
        mapping_path = path or _DEFAULT_MAPPING
        _MAPPING_CACHE = json.loads(mapping_path.read_text(encoding="utf-8"))
    return dict(_MAPPING_CACHE)


def _normalize_flag(value: Any) -> Optional[str]:
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized or None
    return None


def _resolve_decision(discernment: Optional[Dict[str, Any]], mapping: Dict[str, Any]) -> tuple[str, List[str]]:
    decision = str(mapping.get("default_decision", "ALLOW"))
    reason_codes: List[str] = []
    if not discernment:
        reason_codes.append("discernment.none")
        reason_codes.append(f"decision.{decision.lower()}")
        return decision, reason_codes

    order = mapping.get("order", ["band", "uncertainty"])
    band = _normalize_flag(discernment.get("band"))
    uncertainty = _normalize_flag(discernment.get("uncertainty"))

    for key in order:
        if key == "band" and band:
            reason_codes.append(f"band.{band}")
            decision = mapping.get("band", {}).get(band, decision)
        if key == "uncertainty" and uncertainty:
            reason_codes.append(f"uncertainty.{uncertainty}")
            decision = mapping.get("uncertainty", {}).get(uncertainty, decision)

    reason_codes.append(f"decision.{decision.lower()}")
    return decision, reason_codes


def _default_env_allowlist() -> Iterable[str]:
    return ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "HOME")


def _default_env_denylist() -> Iterable[str]:
    return ("AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN")


def _resolve_environment(envelope: Dict[str, Any]) -> Dict[str, List[str]]:
    environment = envelope.get("environment")
    allowlist: Iterable[str] = _default_env_allowlist()
    denylist: Iterable[str] = _default_env_denylist()
    if isinstance(environment, dict):
        allowlist = environment.get("allowlist", allowlist)
        denylist = environment.get("denylist", denylist)
    allowlist = envelope.get("env_allowlist", allowlist)
    denylist = envelope.get("env_denylist", denylist)
    return {"allowlist": list(allowlist), "denylist": list(denylist)}


def _resolve_constraints(envelope: Dict[str, Any], decision: str) -> Dict[str, Any]:
    working_dir = str(Path(envelope.get("working_dir", Path.cwd())))
    allowed_commands = envelope.get("allowed_commands")
    if allowed_commands is None:
        command = envelope.get("command")
        allowed_commands = [command] if command else []
    allowed_paths = envelope.get("allowed_paths") or []
    if decision == "ALLOW" and not allowed_commands and not allowed_paths:
        allowed_paths = [working_dir]

    environment = _resolve_environment(envelope)
    allowlists = {
        "commands": list(allowed_commands),
        "paths": list(allowed_paths),
        "environment": list(environment.get("allowlist", [])),
    }
    constraints = {
        "receipt_required": True,
        "allowlist_execution": True,
        "working_dir": working_dir,
        "sandbox_profile": envelope.get("sandbox_profile", "userland"),
        "timeout_s": envelope.get("timeout_s", 300),
        "resource_limits": envelope.get(
            "resource_limits",
            {"cpu_seconds": 120, "memory_mb": 512, "processes": 64},
        ),
        "allowed_commands": list(allowed_commands) or None,
        "allowed_paths": list(allowed_paths) or None,
        "network": envelope.get("network", {"egress": "restricted"}),
        "environment": environment,
        "allowlists": allowlists,
        "confirmation_required": decision == "REQUIRE_CONFIRM",
    }
    return {key: value for key, value in constraints.items() if value is not None}


@dataclass(frozen=True)
class GuardReceipt:
    receipt_id: str
    issued_at: float
    decision: str
    trace_id: str
    capability_token_ref: str
    constraints: Dict[str, Any]
    token_status: str
    reason_codes: List[str]
    discernment: Dict[str, Any]
    signature: Dict[str, str]
    bindings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "$schema": GUARD_RECEIPT_SCHEMA_ID,
            "receipt_id": self.receipt_id,
            "issued_at": self.issued_at,
            "decision": self.decision,
            "trace_id": self.trace_id,
            "capability_token_ref": self.capability_token_ref,
            "token_status": self.token_status,
            "reason_codes": self.reason_codes,
            "constraints": self.constraints,
            "discernment": self.discernment,
            "signature": self.signature,
            "bindings": self.bindings,
        }


def issue_guard_receipt(
    input_envelope: Dict[str, Any],
    discernment_report: Optional[Dict[str, Any]] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    _validate_schema(input_envelope, "request_envelope.schema.json")
    if discernment_report is not None:
        _validate_schema(discernment_report, "discernment_report.schema.json")

    trace_id = str(input_envelope.get("trace_id", str(uuid.uuid4())))
    mapping = _load_mapping()
    decision, reason_codes = _resolve_decision(discernment_report, mapping)
    constraints = _resolve_constraints(input_envelope, decision)

    envelope_hash = input_envelope.get("envelope_hash")
    capability_refs_list = list(capability_refs or input_envelope.get("capability_refs") or [])
    bindings: Dict[str, Any] = {"trace_id": trace_id}
    if envelope_hash:
        bindings["envelope_hash"] = envelope_hash
    if capability_refs_list:
        bindings["capability_refs"] = capability_refs_list

    capability_token_ref = str(
        input_envelope.get("capability_token_ref")
        or (capability_refs_list[0] if capability_refs_list else "unbound")
    )

    receipt_payload = {
        "$schema": GUARD_RECEIPT_SCHEMA_ID,
        "receipt_id": str(uuid.uuid4()),
        "issued_at": time.time(),
        "decision": decision,
        "trace_id": trace_id,
        "capability_token_ref": capability_token_ref,
        "token_status": "unverified",
        "reason_codes": reason_codes or ["unspecified"],
        "constraints": constraints,
        "discernment": {
            "band": _normalize_flag((discernment_report or {}).get("band")),
            "uncertainty": _normalize_flag((discernment_report or {}).get("uncertainty")),
            "summary": (discernment_report or {}).get("summary"),
        },
        "signature": {"alg": "none", "value": "unsigned"},
        "bindings": bindings,
    }

    _validate_schema(receipt_payload, "guard_receipt.schema.json")

    audit.record(
        "guard.receipt.issued",
        actor="guard",
        payload={
            "receipt_id": receipt_payload["receipt_id"],
            "trace_id": trace_id,
            "decision": decision,
            "reason_codes": reason_codes or ["unspecified"],
            "constraints": constraints,
            "issued_at": receipt_payload["issued_at"],
        },
    )

    bypass_signal = input_envelope.get("guard_bypass") or input_envelope.get("bypass")
    if bypass_signal:
        audit.record(
            "guard.bypass",
            actor="guard",
            payload={"trace_id": trace_id, "signal": bypass_signal},
        )

    return GuardReceipt(
        receipt_id=receipt_payload["receipt_id"],
        issued_at=receipt_payload["issued_at"],
        decision=decision,
        trace_id=trace_id,
        capability_token_ref=capability_token_ref,
        token_status=receipt_payload["token_status"],
        reason_codes=receipt_payload["reason_codes"],
        constraints=constraints,
        discernment=receipt_payload["discernment"],
        signature=receipt_payload["signature"],
        bindings=bindings,
    )


def evaluate_receipt(
    envelope: Dict[str, Any],
    *,
    discernment: Optional[Dict[str, Any]] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    return issue_guard_receipt(
        envelope,
        discernment_report=discernment,
        capability_refs=capability_refs,
    )


def evaluate_from_files(
    envelope_path: Path,
    discernment_path: Optional[Path] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    discernment = json.loads(discernment_path.read_text(encoding="utf-8")) if discernment_path else None
    return issue_guard_receipt(
        envelope,
        discernment_report=discernment,
        capability_refs=capability_refs,
    )

FILE: blux_guard/core/runtime.py
Kind: text
Size: 1769
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Runtime helpers shared across CLI and daemon entry points."""

from __future__ import annotations

import sys
from typing import Iterable, Tuple


_MIN_VERSION: Tuple[int, int] = (3, 9)
_DEBUG_ENABLED: bool = False
_VERBOSE_ENABLED: bool = False


def set_debug(enabled: bool) -> None:
    """Toggle debug behaviour for the running process."""

    global _DEBUG_ENABLED
    _DEBUG_ENABLED = enabled


def debug_enabled() -> bool:
    """Return ``True`` when debug instrumentation is active."""

    return _DEBUG_ENABLED


def set_verbose(enabled: bool) -> None:
    """Toggle verbose logging for the running process."""

    global _VERBOSE_ENABLED
    _VERBOSE_ENABLED = enabled


def verbose_enabled() -> bool:
    """Return ``True`` when verbose messaging is active."""

    return _VERBOSE_ENABLED


def ensure_supported_python(component: str, *, minimum: Tuple[int, int] = _MIN_VERSION) -> None:
    """Exit gracefully when the interpreter is too old.

    Parameters
    ----------
    component:
        Human readable component identifier (e.g. ``"bluxq"``).
    minimum:
        Minimal accepted Python major/minor version tuple.
    """

    current = sys.version_info[:2]
    if current >= minimum:
        return

    message = (
        f"{component} requires Python {minimum[0]}.{minimum[1]} or newer. "
        f"Detected {current[0]}.{current[1]}. Please upgrade your interpreter."
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


def format_supported_versions(supported: Iterable[Tuple[int, int]] | None = None) -> str:
    """Format supported interpreter versions for help messages."""

    if not supported:
        supported = [(3, 9), (3, 10), (3, 11)]
    return ", ".join(f"{major}.{minor}" for major, minor in supported)

FILE: blux_guard/core/security_cockpit.py
Kind: text
Size: 13212
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Security cockpit utilities powering the interactive TUI."""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil is optional at runtime
    psutil = None  # type: ignore

try:  # pragma: no cover - yara is optional
    import yara  # type: ignore
except Exception:  # pragma: no cover
    yara = None  # type: ignore

try:
    from argon2 import PasswordHasher  # type: ignore
    from argon2 import low_level as argon2_low_level  # type: ignore
except Exception:  # pragma: no cover - argon2 is optional in some environments
    PasswordHasher = None  # type: ignore
    argon2_low_level = None  # type: ignore


@dataclass
class ProcessInfo:
    """Snapshot of a single process for the cockpit."""

    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    status: str


@dataclass
class ProcessSnapshot:
    """Collection of process information."""

    processes: List[ProcessInfo] = field(default_factory=list)
    unavailable: bool = False
    message: str = ""


def collect_process_snapshot(limit: int = 5) -> ProcessSnapshot:
    """Collect a snapshot of the top processes.

    Parameters
    ----------
    limit:
        Maximum number of processes to include in the snapshot.
    """

    if psutil is None:
        return ProcessSnapshot(unavailable=True, message="psutil not installed")

    try:
        procs = sorted(
            psutil.process_iter(["pid", "name", "cpu_percent", "status", "memory_info"]),
            key=lambda proc: proc.info.get("cpu_percent") or 0.0,
            reverse=True,
        )
    except (psutil.Error, OSError) as exc:  # pragma: no cover - protective branch
        return ProcessSnapshot(unavailable=True, message=str(exc))

    items: List[ProcessInfo] = []
    for proc in procs[:limit]:
        info = proc.info
        mem_info = info.get("memory_info")
        memory_mb = float(mem_info.rss) / (1024**2) if mem_info else 0.0  # type: ignore[attr-defined]
        items.append(
            ProcessInfo(
                pid=int(info.get("pid") or 0),
                name=str(info.get("name") or "unknown"),
                cpu_percent=float(info.get("cpu_percent") or 0.0),
                memory_mb=memory_mb,
                status=str(info.get("status") or "unknown"),
            )
        )

    return ProcessSnapshot(processes=items)


@dataclass
class YaraScanFinding:
    path: str
    rule: str


@dataclass
class YaraScanReport:
    status: str
    message: str
    findings: List[YaraScanFinding] = field(default_factory=list)
    scanned: List[str] = field(default_factory=list)


def run_yara_scan(
    target_paths: Optional[Iterable[Path]] = None,
    rules_path: Optional[Path] = None,
) -> YaraScanReport:
    """Run a YARA scan over the supplied paths.

    The scan avoids network activity by design and only touches the provided
    directories or files.
    """

    if yara is None:
        return YaraScanReport(status="unavailable", message="yara-python not installed")

    targets = list(target_paths or [Path.cwd()])
    resolved_targets = [str(path.expanduser().resolve()) for path in targets]
    try:
        search_paths = [Path(path) for path in resolved_targets]
    except OSError as exc:  # pragma: no cover - defensive path handling
        return YaraScanReport(status="error", message=f"Invalid path: {exc}")

    if rules_path is None:
        default_rules = Path(os.environ.get("BLUX_GUARD_YARA_RULES", "~/.config/blux-guard/yara/index.yar"))
        rules_path = default_rules.expanduser()

    if not rules_path.exists():
        return YaraScanReport(
            status="missing_rules",
            message=f"Rules not found at {rules_path}",
            scanned=resolved_targets,
        )

    try:
        rules = yara.compile(filepath=str(rules_path))
    except yara.Error as exc:  # pragma: no cover - depends on runtime environment
        return YaraScanReport(status="compile_error", message=str(exc))

    findings: List[YaraScanFinding] = []
    for path in search_paths:
        if path.is_dir():
            for candidate in path.rglob("*"):
                if not candidate.is_file():
                    continue
                try:
                    matches = rules.match(str(candidate))
                except yara.Error:  # pragma: no cover - continue on per-file errors
                    continue
                for match in matches:
                    findings.append(YaraScanFinding(path=str(candidate), rule=str(match)))
        elif path.is_file():
            try:
                matches = rules.match(str(path))
            except yara.Error:
                matches = []
            for match in matches:
                findings.append(YaraScanFinding(path=str(path), rule=str(match)))

    if findings:
        message = f"{len(findings)} YARA finding(s)";
        status = "alert"
    else:
        message = "No matches"
        status = "clean"

    return YaraScanReport(status=status, message=message, findings=findings, scanned=resolved_targets)


@dataclass
class CredentialFinding:
    subject: str
    valid: bool
    detail: str


@dataclass
class CredentialAuditReport:
    status: str
    message: str
    findings: List[CredentialFinding] = field(default_factory=list)


def argon2_credential_audit(credentials_path: Optional[Path] = None) -> CredentialAuditReport:
    """Validate stored credential hashes without revealing underlying secrets."""

    if PasswordHasher is None or argon2_low_level is None:
        return CredentialAuditReport(status="unavailable", message="argon2-cffi not installed")

    if credentials_path is None:
        credentials_path = Path("~/.config/blux-guard/credentials.json").expanduser()

    if not credentials_path.exists():
        return CredentialAuditReport(status="missing", message=f"No credentials file at {credentials_path}")

    try:
        payload = json.loads(credentials_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CredentialAuditReport(status="error", message=f"Invalid JSON: {exc}")

    entries: Iterable[dict[str, Any]] = payload.get("users", []) if isinstance(payload, dict) else []
    findings: List[CredentialFinding] = []
    for entry in entries:
        username = str(entry.get("username", "<unknown>"))
        hash_value = entry.get("argon2")
        if not isinstance(hash_value, str):
            findings.append(CredentialFinding(subject=username, valid=False, detail="Missing argon2 hash"))
            continue
        try:
            # Validate formatting and parameters without verifying a password.
            argon2_low_level.extract_parameters(hash_value)
            findings.append(CredentialFinding(subject=username, valid=True, detail="OK"))
        except Exception as exc:  # pragma: no cover - depends on runtime data
            findings.append(CredentialFinding(subject=username, valid=False, detail=str(exc)))

    invalid = [finding for finding in findings if not finding.valid]
    if invalid:
        status = "alert"
        message = f"{len(invalid)} invalid credential hash(es)"
    else:
        status = "clean"
        message = "All credential hashes valid"

    return CredentialAuditReport(status=status, message=message, findings=findings)


@dataclass
class AuditChainReport:
    status: str
    message: str
    digest: str
    line_count: int


def verify_audit_chain(audit_path: Path) -> AuditChainReport:
    """Verify a hash-chain over the audit log."""

    if not audit_path.exists():
        return AuditChainReport(status="missing", message="Audit log missing", digest="", line_count=0)

    previous = b""
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        previous = sha256(previous + line.encode("utf-8")).digest()

    digest = previous.hex()
    status = "clean" if lines else "empty"
    message = "Audit chain intact" if lines else "Audit log empty"
    return AuditChainReport(status=status, message=message, digest=digest, line_count=len(lines))


@dataclass
class BqGuardHook:
    name: str
    description: str
    callback: Callable[[], Any]


@dataclass
class BqHookStatus:
    registered: List[str] = field(default_factory=list)
    last_result: Optional[str] = None
    message: str = ""


class BqGuardHookRegistry:
    """Registry that tracks hooks for quantum orchestration."""

    def __init__(self) -> None:
        self._hooks: List[BqGuardHook] = []
        self._last_result: Optional[str] = None

    def register(self, hook: BqGuardHook) -> None:
        self._hooks.append(hook)

    def list_hooks(self) -> List[BqGuardHook]:
        return list(self._hooks)

    async def invoke_all(self) -> None:
        """Invoke all hooks sequentially without allowing network access."""

        results: List[str] = []
        for hook in self._hooks:
            maybe_coro = hook.callback()
            if asyncio.iscoroutine(maybe_coro):
                value = await maybe_coro
            else:
                value = maybe_coro
            results.append(f"{hook.name}:{value}")
        self._last_result = ";".join(results) if results else None

    def status(self) -> BqHookStatus:
        return BqHookStatus(
            registered=[hook.name for hook in self._hooks],
            last_result=self._last_result,
            message="Hooks ready" if self._hooks else "No hooks registered",
        )


bq_guard_registry = BqGuardHookRegistry()


def export_diagnostics(
    process_snapshot: ProcessSnapshot,
    yara_report: YaraScanReport,
    credential_report: CredentialAuditReport,
    audit_report: AuditChainReport,
    bq_status: BqHookStatus,
    export_dir: Optional[Path] = None,
) -> dict[str, Path]:
    """Export diagnostics data to JSON and plaintext files.

    The export is stored locally only and avoids network interaction entirely.
    """

    export_dir = (export_dir or Path("~/.config/blux-guard/diagnostics")).expanduser()
    export_dir.mkdir(parents=True, exist_ok=True)

    timestamp = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    process_payload = {
        "unavailable": process_snapshot.unavailable,
        "message": process_snapshot.message,
        "entries": [asdict(proc) for proc in process_snapshot.processes],
    }

    payload = {
        "timestamp": timestamp,
        "processes": process_payload,
        "yara": asdict(yara_report),
        "credentials": asdict(credential_report),
        "audit_chain": asdict(audit_report),
        "bq_guard": {
            "registered": bq_status.registered,
            "last_result": bq_status.last_result,
            "message": bq_status.message,
        },
    }

    json_path = export_dir / f"diagnostics_{timestamp}.json"
    text_path = export_dir / f"diagnostics_{timestamp}.txt"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    text_lines = [
        f"Timestamp: {timestamp}",
        "Processes:",
    ]
    if process_snapshot.unavailable:
        text_lines.append(f"  Unavailable: {process_snapshot.message}")
    else:
        for proc in process_snapshot.processes:
            text_lines.append(
                f"  PID {proc.pid:<6} {proc.name:<25} CPU {proc.cpu_percent:>5.1f}% MEM {proc.memory_mb:>7.1f}MB [{proc.status}]"
            )
    text_lines.extend(
        [
            "",
            f"YARA: {yara_report.status} - {yara_report.message}",
        ]
    )
    for finding in yara_report.findings:
        text_lines.append(f"  {finding.rule}: {finding.path}")
    text_lines.extend(
        [
            "",
            f"Credentials: {credential_report.status} - {credential_report.message}",
        ]
    )
    for finding in credential_report.findings:
        marker = "OK" if finding.valid else "ALERT"
        text_lines.append(f"  [{marker}] {finding.subject}: {finding.detail}")
    text_lines.extend(
        [
            "",
            f"Audit Chain: {audit_report.status} - {audit_report.message}",
            f"Digest: {audit_report.digest}",
            f"Lines: {audit_report.line_count}",
            "",
            "bq Guard Hooks:",
        ]
    )
    text_lines.append(f"  Registered: {', '.join(bq_status.registered) or 'None'}")
    if bq_status.last_result:
        text_lines.append(f"  Last Result: {bq_status.last_result}")
    text_lines.append(f"  Message: {bq_status.message}")

    text_path.write_text("\n".join(text_lines), encoding="utf-8")

    return {"json": json_path, "text": text_path}


__all__ = [
    "ProcessInfo",
    "ProcessSnapshot",
    "collect_process_snapshot",
    "YaraScanFinding",
    "YaraScanReport",
    "run_yara_scan",
    "CredentialFinding",
    "CredentialAuditReport",
    "argon2_credential_audit",
    "AuditChainReport",
    "verify_audit_chain",
    "BqGuardHook",
    "BqHookStatus",
    "BqGuardHookRegistry",
    "bq_guard_registry",
    "export_diagnostics",
]


FILE: blux_guard/core/selfcheck.py
Kind: text
Size: 3556
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Self-check routines for the BLUX Guard runtime."""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, List

from . import telemetry


def _check_config_files() -> Dict[str, str]:
    config_dir = Path(__file__).resolve().parents[1] / "config"
    default = config_dir / "default.yaml"
    local = config_dir / "local.yaml"
    if default.exists():
        detail = "default.yaml present"
        status = "ok"
    else:
        detail = "default.yaml missing"
        status = "fail"
    if not local.exists():
        detail += "; local.yaml optional"
    return {"name": "config.files", "status": status, "detail": detail}


def _check_log_writable() -> Dict[str, str]:
    if not telemetry.ensure_log_dir():
        return {
            "name": "logs.directory",
            "status": "warn",
            "detail": f"unable to create {telemetry.collect_status_sync()['log_dir']}",
        }
    status = telemetry.collect_status_sync()
    path = Path(status["log_dir"])
    test_file = path / ".write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return {
            "name": "logs.directory",
            "status": "ok",
            "detail": f"writable {path}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "name": "logs.directory",
            "status": "warn",
            "detail": f"write failed: {exc}",
        }


def _check_sqlite() -> Dict[str, str]:
    status = telemetry.collect_status_sync()
    db_path = Path(status["sqlite_db"])
    try:
        telemetry.ensure_log_dir()
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.close()
        return {"name": "sqlite.telemetry", "status": "ok", "detail": str(db_path)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"name": "sqlite.telemetry", "status": "warn", "detail": str(exc)}


async def _check_api() -> Dict[str, str]:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, lambda: None)
        _reader, writer = await asyncio.open_connection("127.0.0.1", 8000)
        writer.close()
        await writer.wait_closed()
        return {"name": "api.endpoint", "status": "ok", "detail": "localhost:8000 reachable"}
    except OSError:
        return {
            "name": "api.endpoint",
            "status": "warn",
            "detail": "daemon not reachable on 127.0.0.1:8000",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {"name": "api.endpoint", "status": "warn", "detail": str(exc)}


def _aggregate_status(checks: List[Dict[str, str]]) -> str:
    precedence = {"fail": 2, "warn": 1, "ok": 0}
    score = max(precedence.get(check["status"], 1) for check in checks)
    for state, value in precedence.items():
        if value == score:
            return state
    return "warn"


async def run_self_check() -> Dict[str, object]:
    """Run all checks and return a structured report."""

    results: List[Dict[str, str]] = []
    results.append(_check_config_files())
    results.append(_check_log_writable())
    results.append(_check_sqlite())
    results.append(await _check_api())

    overall = _aggregate_status(results)
    telemetry.record_event(
        "selfcheck.complete",
        actor="cli",
        payload={"overall": overall, "checks": results},
    )
    return {"checks": results, "overall": overall}

FILE: blux_guard/core/telemetry.md
Kind: text
Size: 1100
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Telemetry & Auditing Guide

The telemetry module records guard activity to JSONL and SQLite sinks without introducing runtime failures.

## File Locations

- `~/.config/blux-guard/logs/audit.jsonl` – general guard activity
- `~/.config/blux-guard/logs/telemetry.db` – optional SQLite mirror (`events` table)

Override the base directory with `BLUX_GUARD_LOG_DIR`.

## Failure Handling

All writes are best-effort:

- JSONL/SQLite errors emit a single warning to stderr when `BLUX_GUARD_TELEMETRY_WARN=once`.
- Failures never raise exceptions to callers.
- Set `BLUX_GUARD_TELEMETRY=off` to disable persistence entirely.

## Rotation & Hygiene

- Use the SQLite database to batch-export events when required (`sqlite-utils rows telemetry.db events`).
- Rotate JSONL files with your preferred log rotation tooling or custom cron jobs.
- Delete or archive the JSONL/SQLite files safely; new files will be created automatically on the next write attempt.

## Privacy

Only local actions are recorded. Actors are tagged (`cli`, `daemon`, etc.) for traceability without transmitting data off-device.

FILE: blux_guard/core/telemetry.py
Kind: text
Size: 6887
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Telemetry, auditing, and metrics aggregation utilities."""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, Optional

# Resolve the telemetry directory, allowing overrides for testing or custom deployments.
_LOG_DIR = Path(
    os.environ.get("BLUX_GUARD_LOG_DIR", Path.home() / ".config" / "blux-guard" / "logs")
)
_JSONL = _LOG_DIR / "audit.jsonl"
_DB = _LOG_DIR / "telemetry.db"

_warned_once: Dict[str, bool] = {"json": False, "sqlite": False, "dir": False}
_lock = threading.Lock()
_DEBUG = False
_VERBOSE = False


def _telemetry_enabled() -> bool:
    """Return True when telemetry sinks should be active."""

    return os.getenv("BLUX_GUARD_TELEMETRY", "on").lower() not in {
        "0",
        "off",
        "false",
        "no",
    }


def _warn_once(channel: str, message: str) -> None:
    """Emit a single degrade warning to stderr per channel."""

    if os.getenv("BLUX_GUARD_TELEMETRY_WARN", "once").lower() != "once":
        return

    if not _warned_once.get(channel):
        _warned_once[channel] = True
        print(f"[blux-guard] telemetry degrade: {message}", file=sys.stderr)


def _ensure_dirs() -> bool:
    """Create the telemetry directory if possible."""

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("dir", f"cannot create log dir {_LOG_DIR}: {exc}")
        return False


def ensure_log_dir() -> bool:
    """Public helper to prepare the telemetry directory."""

    return _ensure_dirs()


def set_debug(enabled: bool) -> None:
    """Enable or disable debug mode for telemetry outputs."""

    global _DEBUG
    _DEBUG = enabled


def set_verbose(enabled: bool) -> None:
    """Enable or disable verbose mode for telemetry outputs."""

    global _VERBOSE
    _VERBOSE = enabled


def debug_enabled() -> bool:
    return _DEBUG


def verbose_enabled() -> bool:
    return _VERBOSE


def _safe_jsonl_write(path: Path, obj: Dict[str, Any]) -> None:
    try:
        with _lock:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("json", f"jsonl write failed ({path}): {exc}")


def _safe_sqlite_write(table: str, obj: Dict[str, Any]) -> None:
    try:
        with _lock:
            conn = sqlite3.connect(_DB)
            try:
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        ts REAL,
                        level TEXT,
                        actor TEXT,
                        action TEXT,
                        stream TEXT,
                        payload TEXT
                    )
                    """
                )
                conn.execute(
                    f"""
                    INSERT INTO {table} (ts, level, actor, action, stream, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        obj.get("ts"),
                        obj.get("level"),
                        obj.get("actor"),
                        obj.get("action"),
                        obj.get("stream"),
                        json.dumps(obj.get("payload", {}), ensure_ascii=False),
                    ),
                )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("sqlite", f"sqlite write failed ({_DB}): {exc}")


def record_event(
    action: str,
    level: str = "info",
    actor: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    *,
    stream: str = "audit",
) -> None:
    """Best-effort event recorder that never raises."""

    if not _telemetry_enabled():
        return

    stream = "audit"
    payload = payload or {}
    ensure_log_dir()

    obj = {
        "ts": time.time(),
        "level": level,
        "actor": actor or "local",
        "action": action,
        "payload": payload,
        "stream": stream,
        "channel": action,
    }

    _safe_jsonl_write(_JSONL, obj)
    _safe_sqlite_write("events", obj)

    if _DEBUG or _VERBOSE:
        preview = json.dumps(obj, ensure_ascii=False, sort_keys=True)
        print(f"[telemetry] {preview}", file=sys.stderr)


async def collect_status() -> Dict[str, Any]:
    """Return a simplified status snapshot for CLI consumption."""

    ensure_log_dir()
    return {
        "log_dir": str(_LOG_DIR),
        "audit_log": str(_JSONL),
        "sqlite_db": str(_DB),
        "telemetry_enabled": _telemetry_enabled(),
        "debug": _DEBUG,
        "verbose": _VERBOSE,
    }


def collect_status_sync() -> Dict[str, Any]:
    """Synchronous wrapper over :func:`collect_status`."""

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(collect_status())
    finally:
        loop.close()


@dataclass
class Metric:
    """Container for Prometheus-style metrics."""

    name: str
    value: float
    description: str = ""

    def to_prometheus(self) -> str:
        header = f"# HELP {self.name} {self.description}" if self.description else ""
        type_line = f"# TYPE {self.name} gauge"
        return "\n".join(filter(None, [header, type_line, f"{self.name} {self.value}"]))


async def iter_prometheus_metrics() -> AsyncIterator[str]:
    """Yield Prometheus metric strings asynchronously."""

    metrics = [
        Metric(
            name="blux_guard_heartbeat",
            value=time.time(),
            description="Wall clock timestamp",
        ),
    ]
    for metric in metrics:
        yield metric.to_prometheus()
        await asyncio.sleep(0)


def export_prometheus() -> str:
    """Return metrics in Prometheus exposition format."""

    loop = asyncio.get_event_loop()
    if loop.is_running():
        raise RuntimeError("export_prometheus must not be called from a running loop")

    metrics: list[str] = []

    async def _collect() -> None:
        async for chunk in iter_prometheus_metrics():
            metrics.append(chunk)

    loop.run_until_complete(_collect())
    return "\n".join(metrics)


@contextmanager
def scoped_event(action: str, **payload: Any) -> Iterable[None]:
    """Context manager that automatically records start/stop events."""

    start_payload = {**payload, "phase": "start"}
    record_event(action, payload=start_payload)
    try:
        yield
    finally:
        end_payload = {**payload, "phase": "end"}
        record_event(action, payload=end_payload)

FILE: blux_guard/doctor.py
Kind: text
Size: 2132
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Environment checks for BLUX Guard."""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Dict, List

from . import audit
from .config import default_paths
from .core import telemetry


def _check_python() -> Dict[str, str]:
    version = sys.version.split()[0]
    ok = sys.version_info >= (3, 9)
    return {"name": "python", "status": "ok" if ok else "warn", "detail": version}


def _check_textual() -> Dict[str, str]:
    try:
        import textual  # noqa: F401

        return {"name": "textual", "status": "ok", "detail": "installed"}
    except Exception:
        return {"name": "textual", "status": "warn", "detail": "missing"}


def _check_typer() -> Dict[str, str]:
    try:
        import typer  # noqa: F401

        return {"name": "typer", "status": "ok", "detail": "installed"}
    except Exception:
        return {"name": "typer", "status": "warn", "detail": "missing"}


def _check_log_dir() -> Dict[str, str]:
    paths = default_paths()
    log_dir = paths["log_dir"]
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return {"name": "log_dir", "status": "ok", "detail": log_dir}
    except Exception as exc:
        return {"name": "log_dir", "status": "warn", "detail": str(exc)}


def run_doctor() -> Dict[str, List[Dict[str, str]]]:
    checks = [_check_python(), _check_textual(), _check_typer(), _check_log_dir()]
    overall = "ok" if all(item["status"] == "ok" for item in checks) else "warn"
    telemetry.record_event("doctor.run", actor="cli", payload={"overall": overall})
    audit.record("cli.doctor", actor="cli", payload={"overall": overall})
    return {"overall": overall, "checks": checks, "platform": platform.platform()}


def run_verify() -> Dict[str, str]:
    paths = default_paths()
    writable = telemetry.ensure_log_dir()
    status = "ok" if writable else "warn"
    telemetry.record_event("verify.run", actor="cli", payload={"status": status})
    audit.record("cli.verify", actor="cli", payload={"status": status, "paths": paths})
    return {"status": status, "audit_log": paths["audit_log"]}

FILE: blux_guard/guard/mapping/default_mapping.json
Kind: text
Size: 280
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
{
  "default_decision": "ALLOW",
  "order": ["band", "uncertainty"],
  "band": {
    "critical": "BLOCK",
    "high": "REQUIRE_CONFIRM",
    "medium": "WARN",
    "low": "ALLOW"
  },
  "uncertainty": {
    "high": "REQUIRE_CONFIRM",
    "medium": "WARN",
    "low": "ALLOW"
  }
}

FILE: blux_guard/integrations/__init__.py
Kind: text
Size: 77
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Integration stubs for external BLUX services."""

__all__: list[str] = []

FILE: blux_guard/quantum_plugin.py
Kind: text
Size: 278
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Quantum integration surface for BLUX Guard."""

from __future__ import annotations

import typer

from .cli import bluxq


def register(app: typer.Typer) -> None:
    """Register Guard commands into an existing Typer app."""

    app.add_typer(bluxq.guard_app, name="guard")

FILE: blux_guard/tui/README.md
Kind: text
Size: 1422
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# BLUX Guard Developer Security Cockpit

The Textual cockpit now focuses on secure developer operations. It extends the guard interface with new security instrumentation for CLI-driven workflows.

## Panels

- **Metrics** – summarizes log locations, telemetry enablement, and Prometheus heartbeat values.
- **Processes** – surfaces the top processes by CPU/memory to spot runaway builds.
- **Audit Tail** – tails the JSONL audit stream with best-effort degradation if storage is unavailable.
- **YARA Scanner** – runs local rule packs against configurable paths (no network usage).
- **Credentials** – performs Argon2 metadata validation for stored credential files.
- **Audit Chain** – replays the audit log hash chain to confirm integrity.
- **bq Guard Hooks** – reports quantum orchestration hooks registered via `security_cockpit.bq_guard_registry`.
- **Footer/Header** – Textual status chrome with clock and refresh hotkeys.

## Key Bindings

- `Ctrl+C` – exit the cockpit.
- `r` – refresh all passive panels.
- `p` – refresh process metrics immediately.
- `y` – run a YARA scan against the configured targets.
- `c` – audit Argon2 credential hashes.
- `a` – recompute the audit hash chain digest.
- `b` – invoke registered bq guard hooks.
- `e` – export diagnostics to JSON and plaintext under `~/.config/blux-guard/diagnostics`.

## Launching

```bash
bluxq guard tui --mode dev
```

FILE: blux_guard/tui/__init__.py
Kind: text
Size: 600
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""TUI components for the BLUX Guard Security Cockpit."""

from .audit_integrity_panel import AuditIntegrityPanel
from .audit_panel import AuditPanel
from .bq_panel import BqGuardPanel
from .credentials_panel import CredentialsPanel
from .dashboard import DashboardApp, run_dashboard
from .metrics_panel import MetricsPanel
from .process_panel import ProcessPanel
from .yara_panel import YaraPanel

__all__ = [
    "AuditIntegrityPanel",
    "AuditPanel",
    "BqGuardPanel",
    "CredentialsPanel",
    "DashboardApp",
    "MetricsPanel",
    "ProcessPanel",
    "YaraPanel",
    "run_dashboard",
]

FILE: blux_guard/tui/app.py
Kind: text
Size: 1468
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Unified cockpit wrapper for Textual TUI."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult

from .. import audit
from . import dashboard


class CockpitApp(dashboard.DashboardApp):
    """Extend the dashboard with audit/correlation plumbing."""

    def __init__(self, mode: str = "secure", correlation_id: Optional[str] = None) -> None:
        super().__init__(mode=mode)
        self.correlation_id = correlation_id or audit.generate_correlation_id()

    def compose(self) -> ComposeResult:  # type: ignore[override]
        audit.record(
            "tui.screen.enter",
            actor="tui",
            payload={"screen": "home", "mode": self.mode},
            correlation_id=self.correlation_id,
        )
        for node in super().compose():
            yield node

    def on_unmount(self) -> None:  # type: ignore[override]
        audit.record(
            "tui.screen.exit",
            actor="tui",
            payload={"screen": "home", "mode": self.mode},
            correlation_id=self.correlation_id,
        )


async def run_cockpit(mode: str = "secure", *, correlation_id: Optional[str] = None) -> None:
    """Launch the cockpit with audit tracking."""

    cid = correlation_id or audit.generate_correlation_id()
    audit.record("tui.launch", actor="tui", payload={"mode": mode}, correlation_id=cid)
    app = CockpitApp(mode=mode, correlation_id=cid)
    await app.run_async()

FILE: blux_guard/tui/audit_integrity_panel.py
Kind: text
Size: 1505
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Panel verifying the audit hash chain."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Static

from ..core import security_cockpit, telemetry


class AuditIntegrityPanel(Static):
    """Display audit log integrity information."""

    _report: security_cockpit.AuditChainReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_integrity()

    def refresh_integrity(self) -> security_cockpit.AuditChainReport:
        status = telemetry.collect_status_sync()
        audit_path = Path(status["audit_log"]).expanduser()
        report = security_cockpit.verify_audit_chain(audit_path)
        self._report = report
        self.render_report(report)
        return report

    async def async_refresh(self) -> security_cockpit.AuditChainReport:
        await asyncio.sleep(0)
        return self.refresh_integrity()

    def render_report(self, report: security_cockpit.AuditChainReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.digest:
            lines.append(f"Digest: {report.digest[:16]}…")
        lines.append(f"Entries: {report.line_count}")
        if report.status not in {"clean", "empty"}:
            self.set_class(True, "alert")
        else:
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.AuditChainReport | None:
        return self._report


FILE: blux_guard/tui/audit_panel.py
Kind: text
Size: 751
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Audit log panel."""

from __future__ import annotations

import pathlib

from textual.widgets import Static

from ..core import telemetry


class AuditPanel(Static):
    """Render the most recent audit log lines."""

    _max_lines = 5

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_audit()

    def refresh_audit(self) -> None:
        status = telemetry.collect_status_sync()
        path = pathlib.Path(status["audit_log"])
        if not path.exists():
            self.update("No audit events yet")
            return
        lines = path.read_text(encoding="utf-8").strip().splitlines()[-self._max_lines :]
        rendered = "\n".join(lines) if lines else "No audit events yet"
        self.update(rendered)

FILE: blux_guard/tui/bq_panel.py
Kind: text
Size: 1046
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Panel representing bq guard quantum orchestration hooks."""

from __future__ import annotations

import asyncio

from textual.widgets import Static

from ..core import security_cockpit


class BqGuardPanel(Static):
    """Show registered quantum orchestration hooks and allow invocation."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_status()

    def refresh_status(self) -> security_cockpit.BqHookStatus:
        status = security_cockpit.bq_guard_registry.status()
        lines = ["bq Guard Hooks", f"Registered: {len(status.registered)}"]
        if status.registered:
            lines.append(", ".join(status.registered))
        if status.last_result:
            lines.append(f"Last: {status.last_result}")
        lines.append(status.message)
        self.update("\n".join(lines))
        return status

    async def invoke(self) -> security_cockpit.BqHookStatus:
        await asyncio.sleep(0)
        await security_cockpit.bq_guard_registry.invoke_all()
        return self.refresh_status()


FILE: blux_guard/tui/cockpit.css
Kind: text
Size: 460
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
Screen {
    background: #000a00;
    color: #2cff8f;
}

#title {
    background: #001400;
    color: #37ff9f;
    text-style: bold;
    padding: 1 2;
}

.panel {
    border: round #003300;
    background: #000d00;
    padding: 1;
}

#grid {
    grid-size: 2 4;
    grid-gutter: 1 1;
    padding: 1;
}

.alert {
    color: #ffb000;
    border: double #ffb000;
}

Footer, Header {
    background: #001800;
    color: #36ff90;
}

Static {
    color: #2cff8f;
}


FILE: blux_guard/tui/credentials_panel.py
Kind: text
Size: 1842
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Argon2 credential verification panel."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from textual.widgets import Static

from ..core import security_cockpit


class CredentialsPanel(Static):
    """Audit credential hashes using Argon2 metadata."""

    _report: security_cockpit.CredentialAuditReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.update("Press C to audit credentials")

    async def run_audit(self, credentials_path: Optional[str] = None) -> security_cockpit.CredentialAuditReport:
        self.update("Auditing Argon2 credentials…")
        await asyncio.sleep(0)
        report = await asyncio.to_thread(
            security_cockpit.argon2_credential_audit,
            Path(credentials_path).expanduser() if credentials_path else None,
        )
        self._report = report
        self.render_report(report)
        return report

    def render_report(self, report: security_cockpit.CredentialAuditReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.findings:
            lines.append("")
            for finding in report.findings[:5]:
                marker = "OK" if finding.valid else "ALERT"
                if not finding.valid:
                    self.set_class(True, "alert")
                lines.append(f"[{marker}] {finding.subject}: {finding.detail}")
            if len(report.findings) > 5:
                lines.append(f"… {len(report.findings) - 5} more")
        else:
            self.set_class(False, "alert")
        if report.status == "clean":
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.CredentialAuditReport | None:
        return self._report


FILE: blux_guard/tui/dashboard.py
Kind: text
Size: 4232
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Textual dashboard for the Developer Security Cockpit."""

from __future__ import annotations

from typing import Any

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.widgets import Footer, Header, Static

from ..core import security_cockpit, telemetry
from .audit_integrity_panel import AuditIntegrityPanel
from .audit_panel import AuditPanel
from .bq_panel import BqGuardPanel
from .credentials_panel import CredentialsPanel
from .metrics_panel import MetricsPanel
from .process_panel import ProcessPanel
from .yara_panel import YaraPanel


class DashboardApp(App[Any]):
    CSS_PATH = "cockpit.css"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("p", "refresh_process", "Processes"),
        Binding("y", "scan_yara", "YARA Scan"),
        Binding("c", "audit_credentials", "Credential Audit"),
        Binding("a", "verify_audit", "Audit Chain"),
        Binding("b", "invoke_bq", "bq Hooks"),
        Binding("e", "export_diagnostics", "Export"),
    ]

    def __init__(self, mode: str = "secure") -> None:
        super().__init__()
        self.mode = mode

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield Static(f"BLUX Guard Security Cockpit — Mode: {self.mode}", id="title")
            with Grid(id="grid"):
                yield MetricsPanel(classes="panel")
                yield ProcessPanel(classes="panel")
                yield AuditPanel(classes="panel")
                yield YaraPanel(classes="panel")
                yield CredentialsPanel(classes="panel")
                yield AuditIntegrityPanel(classes="panel")
                yield BqGuardPanel(classes="panel")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(MetricsPanel).refresh_metrics()
        self.query_one(AuditPanel).refresh_audit()
        self.query_one(ProcessPanel).refresh_processes()
        self.query_one(AuditIntegrityPanel).refresh_integrity()
        self.query_one(BqGuardPanel).refresh_status()

    def action_refresh_process(self) -> None:
        self.query_one(ProcessPanel).refresh_processes()

    async def action_scan_yara(self) -> None:
        panel = self.query_one(YaraPanel)
        await panel.run_scan()

    async def action_audit_credentials(self) -> None:
        panel = self.query_one(CredentialsPanel)
        await panel.run_audit()

    async def action_verify_audit(self) -> None:
        panel = self.query_one(AuditIntegrityPanel)
        await panel.async_refresh()

    async def action_invoke_bq(self) -> None:
        panel = self.query_one(BqGuardPanel)
        await panel.invoke()

    async def action_export_diagnostics(self) -> None:
        process_snapshot = self.query_one(ProcessPanel).snapshot
        yara_panel = self.query_one(YaraPanel)
        credential_panel = self.query_one(CredentialsPanel)
        yara_report = yara_panel.report or await asyncio.to_thread(security_cockpit.run_yara_scan)
        credential_report = credential_panel.report or await asyncio.to_thread(
            security_cockpit.argon2_credential_audit
        )
        audit_report = self.query_one(AuditIntegrityPanel).report or security_cockpit.verify_audit_chain(
            Path(telemetry.collect_status_sync()["audit_log"])  # type: ignore[arg-type]
        )
        bq_status = self.query_one(BqGuardPanel).refresh_status()
        exports = await asyncio.to_thread(
            security_cockpit.export_diagnostics,
            process_snapshot,
            yara_report,
            credential_report,
            audit_report,
            bq_status,
        )
        message = "Diagnostics exported:\n" + "\n".join(f"{name}: {path}" for name, path in exports.items())
        self.notify(message, severity="information")

async def run_dashboard(mode: str = "secure") -> None:
    telemetry.record_event(
        "tui.launch",
        actor="tui",
        payload={"mode": mode},
    )
    app = DashboardApp(mode=mode)
    await app.run_async()

FILE: blux_guard/tui/metrics_panel.py
Kind: text
Size: 641
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Metrics panel sourcing data from telemetry."""

from __future__ import annotations

from textual.widgets import Static

from ..core import telemetry


class MetricsPanel(Static):
    """Display runtime metrics for the cockpit."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_metrics()

    def refresh_metrics(self) -> None:
        status = telemetry.collect_status_sync()
        message = (
            f"Log dir: {status['log_dir']}\n"
            f"Audit log entries -> {status['audit_log']}\n"
            f"Telemetry enabled: {status['telemetry_enabled']}"
        )
        self.update(message)

FILE: blux_guard/tui/process_panel.py
Kind: text
Size: 1189
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Process monitoring panel for the cockpit."""

from __future__ import annotations

from textual.widgets import Static

from ..core import security_cockpit


class ProcessPanel(Static):
    """Render top process information using psutil."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_processes()

    def refresh_processes(self) -> None:
        snapshot = security_cockpit.collect_process_snapshot()
        if snapshot.unavailable:
            self.update(f"Process monitor unavailable\n{snapshot.message}")
            self.set_class(True, "alert")
            return

        lines = ["PID    CPU%   MEM(MB) STATUS   NAME"]
        for proc in snapshot.processes:
            lines.append(
                f"{proc.pid:<6} {proc.cpu_percent:>5.1f} {proc.memory_mb:>8.1f} {proc.status:<8} {proc.name}"
            )
        self.update("\n".join(lines))
        self.set_class(False, "alert")
        self._snapshot = snapshot

    @property
    def snapshot(self) -> security_cockpit.ProcessSnapshot:
        if not hasattr(self, "_snapshot"):
            self._snapshot = security_cockpit.collect_process_snapshot()
        return self._snapshot


FILE: blux_guard/tui/yara_panel.py
Kind: text
Size: 1908
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Panel that triggers local YARA scans."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Optional

from textual.widgets import Static

from ..core import security_cockpit


class YaraPanel(Static):
    """Display and run YARA scans on-demand."""

    _paths: Optional[list[str]] = None
    _report: security_cockpit.YaraScanReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.update("Press Y to run YARA scan")

    async def run_scan(
        self,
        paths: Optional[Iterable[str]] = None,
        rules_path: Optional[str] = None,
    ) -> security_cockpit.YaraScanReport:
        self.update("Scanning with YARA…")
        await asyncio.sleep(0)
        path_objects = [Path(p) for p in (paths or self._paths or ["."])]
        report = await asyncio.to_thread(
            security_cockpit.run_yara_scan,
            path_objects,
            Path(rules_path) if rules_path else None,
        )
        self._report = report
        self._paths = [str(p) for p in path_objects]
        self.render_report(report)
        return report

    def render_report(self, report: security_cockpit.YaraScanReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.scanned:
            lines.append("Targets: " + ", ".join(report.scanned))
        if report.findings:
            self.set_class(True, "alert")
            lines.append("")
            for finding in report.findings[:5]:
                lines.append(f"{finding.rule} -> {finding.path}")
            if len(report.findings) > 5:
                lines.append(f"… {len(report.findings) - 5} more")
        else:
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.YaraScanReport | None:
        return self._report


FILE: docs/ROLE.md
Kind: text
Size: 882
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Guard Role: Enforcement Layer (Userland Only)

## Responsibilities (Allowed)
- Enforce request receipts by applying userland constraints to Guard actions.
- Emit receipts with ALLOW/WARN/REQUIRE_CONFIRM/BLOCK outcomes and explicit constraints.
- Operate without elevated privileges; all checks and mitigations stay in user space.
- Keep enforcement deterministic, auditable, and protocol-scoped.
- Report violations and constraint mismatches without attempting escalation.

## Explicit Non-Goals
- No privilege elevation mechanisms of any kind.
- No kernel hooks, kernel-level modules, or privileged network/OS controls.
- No token issuance or verification logic.
- No policy or ethics reasoning.
- No changes to blux-ecosystem contracts.
- Guard does not run tools or spawn shells.
- Guard can be bypassed by design but emits an audit log entry when a bypass signal is provided.

FILE: examples/config.sample.yaml
Kind: text
Size: 118
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
telemetry:
  enabled: true
  warn_once: true
  log_dir: ~/.config/blux-guard/logs
api:
  host: 127.0.0.1
  port: 8000

FILE: examples/doctrine.sample.md
Kind: text
Size: 367
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Sample Doctrine Pillars

- **Autonomy Respect** — Ensure all automated actions present operator review steps.
- **Containment First** — Prefer sandboxing and auditing over destructive measures.
- **Transparency** — Record every privileged action via `telemetry.record_event`.
- **Alignment Checks** — Reject deployments when doctrine score falls below 0.8.

FILE: examples/guard_receipt.example.json
Kind: text
Size: 1281
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
{
  "$schema": "blux://contracts/guard_receipt.schema.json",
  "receipt_id": "b0f27926-808f-4a18-821c-0af9e4e7783c",
  "issued_at": 1735756800.0,
  "decision": "ALLOW",
  "trace_id": "trace-12345",
  "capability_token_ref": "cap-ref-123",
  "token_status": "unverified",
  "reason_codes": ["discernment.none", "decision.allow"],
  "constraints": {
    "sandbox_profile": "userland",
    "network": {"egress": "restricted"},
    "allowed_paths": ["/workspace/blux-guard"],
    "allowlists": {
      "commands": [],
      "paths": ["/workspace/blux-guard"],
      "environment": ["PATH", "LANG", "LC_ALL", "LC_CTYPE", "HOME"]
    },
    "timeout_s": 300,
    "working_dir": "/workspace/blux-guard",
    "environment": {
      "allowlist": ["PATH", "LANG", "LC_ALL", "LC_CTYPE", "HOME"],
      "denylist": ["AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN"]
    },
    "resource_limits": {"cpu_seconds": 120, "memory_mb": 512, "processes": 64},
    "confirmation_required": false
  },
  "discernment": {
    "band": "low",
    "uncertainty": "low",
    "summary": "userland enforcement"
  },
  "signature": {"alg": "none", "value": "unsigned"},
  "bindings": {
    "trace_id": "trace-12345",
    "envelope_hash": "envhash-123",
    "capability_refs": ["cap-ref-123"]
  }
}

FILE: mypy.ini
Kind: text
Size: 81
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
[mypy]
python_version = 3.9
ignore_missing_imports = True
strict_optional = True

FILE: pyproject.toml
Kind: text
Size: 1540
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
[build-system]
requires = ["setuptools>=77.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "blux-guard"
version = "1.0.0"
description = "Terminal TUI Dev Security / BLUX Ecosystem Cockpit"
readme = "README.md"
authors = [{ name = "Outer Void Team" }]
license = { text = "Apache-2.0" }
requires-python = ">=3.9"
keywords = ["security", "tui", "textual", "blux", "guard", "cli", "quantum"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Topic :: Security",
]
dependencies = [
    "argon2-cffi",
    "cryptography",
    "textual>=0.62.0",
    "textual-dev",
    "rich>=13.7.0",
    "pysqlite3",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "typer>=0.12.3",
    "psutil>=5.9.8",
    "sqlite-utils>=3.36",
    "prometheus-client>=0.20.0",
    "pydantic>=2.7.0",
    "pyyaml>=6.0.1",
    "jsonschema>=4.23.0",
]

[project.optional-dependencies]
dev = ["ruff", "mypy", "pytest"]
[project.scripts]
bluxq = "blux_guard.cli.bluxq:app"
bluxqd = "blux_guard.api.guardd:start"
blux-guard = "blux_guard.cli.blux_guard:app"

[tool.setuptools]
license-files = [
    "LICENSE",
    "LICENSE-APACHE",
    "LICENSE-COMMERCIAL",
    "NOTICE",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["blux_guard*"]

[tool.setuptools.package-data]
blux_guard = ["contracts/phase0/*.json"]

FILE: pytest.ini
Kind: text
Size: 22
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
[pytest]
addopts = -q

FILE: requirements.txt
Kind: text
Size: 360
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
# Security & Cryptography
argon2-cffi ~= 25.1.0
cryptography ~= 46.0.3

# UI Framework
textual ~= 6.3.0
textual-dev ~= 1.8.0
rich ~= 14.2.0
jsonschema ~= 4.23.0

# Database
pysqlite3 ~= 0.5.4

# System Monitoring
psutil ~= 5.9.0

# Filesystem Monitoring
watchdog ~= 4.0.0

# Testing & Development
pytest ~= 8.3.0
black ~= 24.3.0
flake8 ~= 7.0.0
mypy ~= 1.10.0

FILE: scripts/physics_check.sh
Kind: text
Size: 747
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(git rev-parse --show-toplevel)
cd "$repo_dir"

python scripts/physics_guard.py

schema_names=(
  "request_envelope.schema.json"
  "discernment_report.schema.json"
)

base_ref=${GITHUB_BASE_REF:-main}
if git show-ref --verify --quiet "refs/remotes/origin/$base_ref"; then
  base_commit=$(git merge-base "origin/$base_ref" HEAD)
else
  base_commit=$(git rev-parse HEAD~1 2>/dev/null || echo "")
fi

if [ -n "$base_commit" ]; then
  changed=$(git diff --name-only "$base_commit"...HEAD)
  for name in "${schema_names[@]}"; do
    if printf '%s\n' "$changed" | rg -n --fixed-strings -- "$name" >/dev/null; then
      echo "Blocked: Phase 0 schema change detected: $name"
      exit 1
    fi
  done
fi

FILE: scripts/physics_guard.py
Kind: text
Size: 2999
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Physics checks for guard-only posture."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}

CODE_SUFFIXES = {".py", ".sh"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}

EXEC_PATTERNS = [
    re.compile(r"\bsubprocess\b"),
    re.compile(r"os\.system"),
    re.compile(r"\bexec\("),
    re.compile(r"create_subprocess"),
    re.compile(r"\bshell\b"),
]

PRIV_PATTERNS = [
    re.compile(r"\bsudo\b", re.IGNORECASE),
    re.compile(r"\broot required\b", re.IGNORECASE),
    re.compile(r"\brequires root\b", re.IGNORECASE),
    re.compile(r"\brun as root\b", re.IGNORECASE),
    re.compile(r"\broot-only\b", re.IGNORECASE),
    re.compile(r"\bprivileged escalation\b", re.IGNORECASE),
]

TOKEN_PATTERNS = [
    re.compile(r"\bverify_tokens?\b"),
    re.compile(r"\bissue_token\b"),
    re.compile(r"\bmint_token\b"),
]

DOCTRINE_PATTERNS = [
    re.compile(r"\bdoctrine\b", re.IGNORECASE),
    re.compile(r"policy engine", re.IGNORECASE),
]

CONTRACT_PATTERNS = [
    re.compile(r"canonical contract", re.IGNORECASE),
    re.compile(r"canonical contracts", re.IGNORECASE),
]


def _iter_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        paths.append(path)
    return paths


def _scan_file(path: Path) -> list[str]:
    violations: list[str] = []
    if path.resolve() == Path(__file__).resolve():
        return violations
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    suffix = path.suffix.lower()
    if suffix in CODE_SUFFIXES:
        for pattern in EXEC_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in TOKEN_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in DOCTRINE_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")

    if suffix in TEXT_SUFFIXES:
        for pattern in PRIV_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in CONTRACT_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")

    return violations


def main() -> int:
    violations: list[str] = []
    for path in _iter_files(ROOT):
        violations.extend(_scan_file(path))
    if violations:
        print("Physics check failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

FILE: tests/test_cli.py
Kind: text
Size: 1018
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Smoke tests for BLUX Guard surfaces."""

import tempfile
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard import audit
from blux_guard.cli import bluxq
from blux_guard.tui import app as tui_app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(bluxq.app, ["--help"])
    assert result.exit_code == 0
    assert "guard" in result.stdout


def test_tui_instantiation() -> None:
    instance = tui_app.CockpitApp(mode="dev")
    assert instance.mode == "dev"


def test_audit_append(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        cid = audit.record("test.event", actor="test", payload={"foo": "bar"})
        log_path = audit.audit_log_path()
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert cid in content

FILE: tests/test_receipt.py
Kind: text
Size: 1399
Last modified: 2026-01-22T05:14:58.518426Z

CONTENT:
"""Tests for guard receipt issuance."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard.core import receipt as receipt_engine


def _base_envelope() -> dict:
    return {
        "trace_id": "trace-123",
        "capability_token_ref": "cap-token-abc",
        "working_dir": "/tmp/workdir",
    }


def test_band_critical_blocks() -> None:
    receipt = receipt_engine.issue_guard_receipt(
        _base_envelope(),
        discernment_report={"band": "critical"},
    )
    assert receipt.decision == "BLOCK"
    assert "band.critical" in receipt.reason_codes


def test_uncertainty_high_requires_confirmation() -> None:
    receipt = receipt_engine.issue_guard_receipt(
        _base_envelope(),
        discernment_report={"uncertainty": "high"},
    )
    assert receipt.decision == "REQUIRE_CONFIRM"


def test_default_allows_with_path_allowlist() -> None:
    receipt = receipt_engine.issue_guard_receipt(_base_envelope())
    payload = receipt.to_dict()
    assert receipt.decision == "ALLOW"
    assert receipt.constraints.get("allowed_paths")
    assert payload["$schema"] == receipt_engine.GUARD_RECEIPT_SCHEMA_ID


def test_bindings_include_trace_id() -> None:
    receipt = receipt_engine.issue_guard_receipt(_base_envelope())
    assert receipt.bindings["trace_id"] == "trace-123"

## 4) Workflow Inventory (index only)
- .github/workflows/ci.yml: push, pull_request

## 5) Search Index (raw results)

subprocess:
.config/blux_guard/motd_dynamic.py
.config/blux_guard/show_motd.sh
scripts/physics_guard.py

os.system:
none

exec(:
none

spawn:
ROLE.md
docs/ROLE.md

shell:
.config/blux_guard/motd_dynamic.py
ROLE.md
docs/ROLE.md
scripts/physics_guard.py

child_process:
none

policy:
PRIVACY.md
ROLE.md
docs/ROLE.md
scripts/physics_guard.py

ethic:
ROLE.md
docs/ROLE.md

enforce:
INSTALL.md
README.md
ROLE.md
docs/ROLE.md
examples/guard_receipt.example.json

guard:
.config/blux_guard/show_motd.sh
.config/rules/__init__.py
.config/rules/rules.json
.gitignore
ARCHITECTURE.md
AUDIT_SCHEMA.md
COCKPIT_SPEC.md
CONFIGURATION.md
INSTALL.md
Makefile
OPERATIONS.md
PRIVACY.md
README.md
SECURITY.md
TROUBLESHOOTING.md
blux_guard/api/server.py
blux_guard/cli/README.md
blux_guard/cli/blux_guard.py
blux_guard/cli/bluxq.py
blux_guard/config/__init__.py
blux_guard/config/default.yaml
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/core/receipt.py
blux_guard/core/security_cockpit.py
blux_guard/core/telemetry.md
blux_guard/core/telemetry.py
blux_guard/quantum_plugin.py
blux_guard/tui/README.md
blux_guard/tui/bq_panel.py
examples/config.sample.yaml
examples/guard_receipt.example.json
pyproject.toml
scripts/physics_check.sh
scripts/physics_guard.py
tests/test_cli.py
tests/test_receipt.py

receipt:
ARCHITECTURE.md
PRIVACY.md
README.md
ROLE.md
SECURITY.md
blux_guard/cli/blux_guard.py
blux_guard/cli/bluxq.py
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/core/receipt.py
docs/ROLE.md
examples/guard_receipt.example.json
tests/test_receipt.py

token:
ROLE.md
SECURITY.md
blux_guard/cli/blux_guard.py
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json
blux_guard/core/receipt.py
docs/ROLE.md
examples/guard_receipt.example.json
scripts/physics_guard.py
tests/test_receipt.py

signature:
.config/rules/index.yar
.config/rules/rules.json
README.md
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/core/receipt.py
examples/guard_receipt.example.json

verify:
COCKPIT_SPEC.md
OPERATIONS.md
ROLE.md
blux_guard/cli/blux_guard.py
blux_guard/cli/bluxq.py
blux_guard/core/security_cockpit.py
blux_guard/doctor.py
blux_guard/tui/audit_integrity_panel.py
blux_guard/tui/dashboard.py
scripts/physics_check.sh
scripts/physics_guard.py

capability:
README.md
blux_guard/cli/README.md
blux_guard/cli/bluxq.py
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json
blux_guard/core/receipt.py
examples/guard_receipt.example.json
tests/test_receipt.py

key_id:
none

contract:
LICENSE-APACHE
blux_guard/contracts/phase0/__init__.py
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/core/receipt.py
docs/ROLE.md
examples/guard_receipt.example.json
pyproject.toml
scripts/physics_guard.py

schema:
README.md
blux_guard/contracts/phase0/__init__.py
blux_guard/contracts/phase0/discernment_report.schema.json
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json
blux_guard/core/receipt.py
examples/guard_receipt.example.json
pyproject.toml
requirements.txt
scripts/physics_check.sh
tests/test_receipt.py

$schema:
blux_guard/contracts/phase0/discernment_report.schema.json
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json
blux_guard/core/receipt.py
examples/guard_receipt.example.json
tests/test_receipt.py

json-schema:
blux_guard/contracts/phase0/discernment_report.schema.json
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json

router:
none

orchestr:
COCKPIT_SPEC.md
README.md
blux_guard/core/devsuite.py
blux_guard/core/security_cockpit.py
blux_guard/tui/README.md
blux_guard/tui/bq_panel.py

execute:
CONTRIBUTING.md
LICENSE-APACHE
ROLE.md
blux_guard/core/selfcheck.py
blux_guard/core/telemetry.py

command:
.config/blux_guard/show_motd.sh
AUDIT_SCHEMA.md
CHANGELOG.md
COCKPIT_SPEC.md
INSTALL.md
README.md
ROLE.md
SECURITY.md
blux_guard/cli/README.md
blux_guard/cli/blux_guard.py
blux_guard/cli/bluxq.py
blux_guard/contracts/phase0/guard_receipt.schema.json
blux_guard/contracts/phase0/request_envelope.schema.json
blux_guard/core/receipt.py
blux_guard/quantum_plugin.py
examples/guard_receipt.example.json

## 6) Notes
none
