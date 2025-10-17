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
