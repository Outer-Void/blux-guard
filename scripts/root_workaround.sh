#!/usr/bin/env bash
# BLUX Guard Privilege Workarounds
# Provides fallback if certain tasks require elevated privileges
# Cross-platform: Linux, macOS, Windows (Admin), Termux
# Version: 2.0.0
# Author: Outer Void Team

set -euo pipefail  # Strict error handling
IFS=$'\n\t'

# Script directory resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"
WORKAROUND_LOG="$CONFIG_DIR/workaround_audit.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  INFO:${NC} $1"; }
log_success() { echo -e "${GREEN}✅ SUCCESS:${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠️  WARNING:${NC} $1"; }
log_error() { echo -e "${RED}❌ ERROR:${NC} $1"; }
log_debug() { echo -e "${CYAN}🐛 DEBUG:${NC} $1"; }
log_security() { echo -e "${MAGENTA}🔒 SECURITY:${NC} $1"; }

# Platform detection
get_platform() {
    case "$(uname -s)" in
        Linux*)
            if [ -f /system/bin/adb ] || [ -d /data/data/com.termux ]; then
                echo "termux"
            elif [ -f /etc/redhat-release ]; then
                echo "rhel"
            elif [ -f /etc/debian_version ]; then
                echo "debian"
            else
                echo "linux"
            fi
            ;;
        Darwin*) echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        FreeBSD*) echo "freebsd" ;;
        *) echo "unknown" ;;
    esac
}

# Cross-platform privilege detection
is_elevated() {
    local platform=$(get_platform)
    
    case "$platform" in
        linux|macos|termux|rhel|debian|freebsd)
            [ "$(id -u)" -eq 0 ]
            ;;
        windows)
            net session >/dev/null 2>&1
            ;;
        *)
            # Fallback for unknown platforms
            [ "$(id -u)" -eq 0 ] 2>/dev/null || false
            ;;
    esac
}

# Cross-platform privilege escalation methods
get_privilege_escalator() {
    local platform=$(get_platform)
    
    case "$platform" in
        linux|rhel|debian|freebsd)
            # Prefer sudo, fallback to su or pkexec
            if command -v sudo >/dev/null 2>&1; then
                echo "sudo"
            elif command -v su >/dev/null 2>&1; then
                echo "su"
            elif command -v pkexec >/dev/null 2>&1; then
                echo "pkexec"
            else
                echo "none"
            fi
            ;;
        macos)
            if command -v sudo >/dev/null 2>&1; then
                echo "sudo"
            else
                echo "none"
            fi
            ;;
        windows)
            if command -v runas >/dev/null 2>&1; then
                echo "runas"
            else
                echo "none"
            fi
            ;;
        termux)
            # Termux may have tsu or sudo
            if command -v tsu >/dev/null 2>&1; then
                echo "tsu"
            elif command -v sudo >/dev/null 2>&1; then
                echo "sudo"
            else
                echo "none"
            fi
            ;;
        *)
            echo "none"
            ;;
    esac
}

# Security audit logging
log_privilege_event() {
    local event_type="$1"
    local command="$2"
    local success="$3"
    local platform=$(get_platform)
    local user="${SUDO_USER:-$USER}"
    local timestamp=$(date -Iseconds)
    
    mkdir -p "$CONFIG_DIR"
    echo "[$timestamp] [PLATFORM:$platform] [USER:$user] [EVENT:$event_type] [CMD:$command] [SUCCESS:$success]" >> "$WORKAROUND_LOG"
    
    # Secure the audit log
    if [ "$platform" != "windows" ]; then
        chmod 600 "$WORKAROUND_LOG" 2>/dev/null || true
    fi
}

# Dependency validation
validate_environment() {
    local platform=$(get_platform)
    
    log_info "Validating environment for: $platform"
    
    # Check BLUX root structure
    if [ ! -f "$BLUX_ROOT/blux_modules/__init__.py" ]; then
        log_error "BLUX Guard installation not found or corrupted"
        return 1
    fi
    
    # Platform-specific dependency checks
    case "$platform" in
        windows)
            if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
                log_error "Python not found on Windows"
                log_info "Install Python from: https://www.python.org/downloads/"
                return 1
            fi
            ;;
        termux)
            if ! command -v python >/dev/null 2>&1; then
                log_error "Python not found in Termux"
                log_info "Install with: pkg install python"
                return 1
            fi
            ;;
        *)
            if ! command -v python3 >/dev/null 2>&1; then
                log_error "Python 3 not found"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Safe command execution with privilege escalation
execute_with_privileges() {
    local command="$1"
    local description="$2"
    local required_level="${3:-low}"  # low, medium, high
    
    local platform=$(get_platform)
    local escalator=$(get_privilege_escalator)
    local is_admin=$(is_elevated && echo "true" || echo "false")
    
    log_security "Attempting: $description"
    log_info "Platform: $platform, Privileges: $is_admin, Escalator: $escalator"
    
    # Check if we already have sufficient privileges
    if [ "$is_admin" = "true" ]; then
        log_success "Already running with elevated privileges"
        log_privilege_event "direct_execution" "$command" "true"
        eval "$command"
        return $?
    fi
    
    # For high-security operations, require explicit elevation
    if [ "$required_level" = "high" ] && [ "$escalator" = "none" ]; then
        log_error "High-security operation requires privilege escalation, but no escalator available"
        log_privilege_event "escalation_failed" "$command" "false"
        return 1
    fi
    
    # Attempt privilege escalation
    case "$escalator" in
        sudo)
            log_info "Attempting sudo escalation..."
            if sudo -n true 2>/dev/null; then
                # Password not required (has NOPASSWD in sudoers)
                log_success "Passwordless sudo available"
                log_privilege_event "sudo_nopasswd" "$command" "true"
                sudo bash -c "$command"
                return $?
            else
                log_warning "Interactive sudo required"
                if [ -t 0 ]; then
                    # We have a terminal, can prompt for password
                    log_privilege_event "sudo_interactive" "$command" "true"
                    sudo bash -c "$command"
                    return $?
                else
                    log_error "No terminal available for sudo prompt"
                    log_privilege_event "sudo_no_terminal" "$command" "false"
                    return 1
                fi
            fi
            ;;
        su)
            log_info "Attempting su escalation..."
            if [ -t 0 ]; then
                log_privilege_event "su_interactive" "$command" "true"
                su -c "$command"
                return $?
            else
                log_error "No terminal available for su"
                return 1
            fi
            ;;
        pkexec)
            log_info "Attempting pkexec escalation (GUI)..."
            log_privilege_event "pkexec_attempt" "$command" "true"
            pkexec bash -c "$command"
            return $?
            ;;
        tsu)
            log_info "Attempting tsu escalation (Termux)..."
            log_privilege_event "tsu_attempt" "$command" "true"
            tsu -c "$command"
            return $?
            ;;
        runas)
            log_info "Attempting runas escalation (Windows)..."
            # Windows runas requires different syntax
            log_privilege_event "runas_attempt" "$command" "true"
            if command -v powershell >/dev/null 2>&1; then
                powershell -Command "Start-Process -Verb RunAs -FilePath 'bash' -ArgumentList '-c', '$command'"
            else
                runas /user:Administrator "bash -c '$command'"
            fi
            return $?
            ;;
        none)
            log_warning "No privilege escalation method available"
            
            # Attempt non-privileged fallback
            attempt_non_privileged_fallback "$command" "$description"
            return $?
            ;;
    esac
}

# Non-privileged fallback implementations
attempt_non_privileged_fallback() {
    local command="$1"
    local description="$2"
    
    log_warning "Attempting non-privileged fallback for: $description"
    log_privilege_event "non_privileged_fallback" "$command" "attempt"
    
    # Extract the main action from the command for fallback logic
    local main_action=$(echo "$command" | grep -o 'system-scanner\|install-service\|network-monitor' | head -1)
    
    case "$main_action" in
        system-scanner)
            log_info "Running user-space system scanner..."
            python3 -c "
import sys
sys.path.append('$BLUX_ROOT')
from blux_modules.system_scanner import SystemScanner

scanner = SystemScanner()
# User-space limited scan
results = scanner.scan_user_space()
print('User-space scan completed with limited privileges')
print(f'Scanned {len(results.get(\"items\", []))} user-accessible items')
            "
            ;;
        network-monitor)
            log_info "Running user-space network monitor..."
            python3 -c "
import sys
sys.path.append('$BLUX_ROOT')
try:
    from blux_modules.network_monitor import NetworkMonitor
    monitor = NetworkMonitor()
    # User-space network information
    info = monitor.get_user_network_info()
    print('User-space network monitoring active')
    print(f'Active connections: {len(info.get(\"connections\", []))}')
except Exception as e:
    print(f'Limited network info available: {e}')
"
            ;;
        install-service)
            log_info "Installing user-space service..."
            "$SCRIPT_DIR/install_service.sh" --user-space
            ;;
        *)
            log_error "No fallback available for: $main_action"
            log_privilege_event "no_fallback" "$command" "false"
            return 1
            ;;
    esac
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_warning "Completed with LIMITED functionality (non-privileged)"
        log_privilege_event "fallback_success" "$command" "true"
    else
        log_error "Fallback execution failed"
        log_privilege_event "fallback_failed" "$command" "false"
    fi
    
    return $exit_code
}

# Security warning for elevated operations
show_security_warning() {
    local operation="$1"
    
    echo
    echo -e "${YELLOW}⚠️  SECURITY WARNING: Privilege Escalation${NC}"
    echo "════════════════════════════════════════"
    echo "Operation: $operation"
    echo "Platform: $(get_platform)"
    echo "User: $USER"
    echo
    echo -e "${RED}This operation requires elevated privileges${NC}"
    echo "• Commands will run with root/admin rights"
    echo "• Audit logging is enabled for security"
    echo "• Only continue if you trust this application"
    echo
    read -p "Continue with privilege escalation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operation cancelled by user"
        exit 0
    fi
}

# Platform-specific command generators
generate_system_scan_command() {
    local platform=$(get_platform)
    
    case "$platform" in
        windows)
            echo "python -m blux_modules.system_scanner --platform windows --elevated"
            ;;
        macos)
            echo "python3 -m blux_modules.system_scanner --platform macos --elevated"
            ;;
        termux)
            echo "python -m blux_modules.system_scanner --platform android --elevated"
            ;;
        *)
            echo "python3 -m blux_modules.system_scanner --elevated"
            ;;
    esac
}

generate_network_monitor_command() {
    local platform=$(get_platform)
    
    case "$platform" in
        windows)
            echo "python -m blux_modules.network_monitor --platform windows --elevated"
            ;;
        macos)
            echo "python3 -m blux_modules.network_monitor --platform macos --elevated"
            ;;
        termux)
            echo "python -m blux_modules.network_monitor --platform android --elevated"
            ;;
        *)
            echo "python3 -m blux_modules.network_monitor --elevated"
            ;;
    esac
}

# Main workaround handler
handle_workaround() {
    local operation="$1"
    local security_level="${2:-medium}"
    
    echo -e "${BLUE}"
    echo "🛠️  BLUX Guard Privilege Workarounds v2.0.0"
    echo "════════════════════════════════════════"
    echo -e "${NC}"
    
    # Validate environment first
    if ! validate_environment; then
        exit 1
    fi
    
    # Show security warning for elevated operations
    if [ "$security_level" != "low" ]; then
        show_security_warning "$operation"
    fi
    
    cd "$BLUX_ROOT" || {
        log_error "Cannot access BLUX root directory"
        exit 1
    }
    
    case "$operation" in
        system-scan)
            local scan_command=$(generate_system_scan_command)
            execute_with_privileges "$scan_command" "System Security Scan" "high"
            ;;
            
        install-service)
            local service_script="$SCRIPT_DIR/install_service.sh"
            if [ ! -f "$service_script" ]; then
                log_error "Service installation script not found: $service_script"
                exit 1
            fi
            execute_with_privileges "\"$service_script\" --install" "Service Installation" "high"
            ;;
            
        network-monitor)
            local monitor_command=$(generate_network_monitor_command)
            execute_with_privileges "$monitor_command" "Network Monitoring" "high"
            ;;
            
        user-service)
            log_info "Installing user-space service..."
            "$SCRIPT_DIR/install_service.sh" --user-space
            ;;
            
        security-audit)
            log_info "Running security audit..."
            execute_with_privileges "python3 -m blux_modules.security_engine --audit" "Security Audit" "medium"
            ;;
            
        file-integrity)
            log_info "Running file integrity check..."
            execute_with_privileges "python3 -m blux_modules.anti_tamper --system-scan" "File Integrity Check" "high"
            ;;
            
        firewall-config)
            log_info "Configuring firewall rules..."
            execute_with_privileges "python3 -m blux_modules.network_monitor --configure-firewall" "Firewall Configuration" "high"
            ;;
            
        *)
            log_error "Unknown operation: $operation"
            show_usage
            exit 1
            ;;
    esac
}

# Show usage information
show_usage() {
    local platform=$(get_platform)
    local escalator=$(get_privilege_escalator)
    
    echo "BLUX Guard Privilege Workarounds"
    echo "Usage: $0 [OPERATION] [OPTIONS]"
    echo
    echo "Available Operations:"
    echo "  system-scan      - Comprehensive system security scan (requires elevation)"
    echo "  install-service  - Install BLUX Guard as system service (requires elevation)"
    echo "  network-monitor  - Real-time network monitoring (requires elevation)"
    echo "  user-service     - Install user-space service (no elevation required)"
    echo "  security-audit   - Run security audit and compliance check"
    echo "  file-integrity   - System file integrity verification"
    echo "  firewall-config  - Configure system firewall rules"
    echo
    echo "Platform: $platform"
    echo "Privilege Escalator: $escalator"
    echo "Current User: $USER"
    echo "Elevated: $(is_elevated && echo 'Yes' || echo 'No')"
    echo
    echo "Security Features:"
    echo "  • Cross-platform privilege escalation"
    echo "  • Audit logging for all elevated operations"
    echo "  • Non-privileged fallback modes"
    echo "  • Security warnings and user confirmation"
    echo "  • Platform-specific command optimization"
    echo
    echo "Audit Log: $WORKAROUND_LOG"
}

# Handle command line arguments
case "${1:-}" in
    system-scan|install-service|network-monitor|security-audit|file-integrity|firewall-config)
        handle_workaround "$1" "high"
        ;;
    user-service)
        handle_workaround "$1" "low"
        ;;
    --audit-log)
        if [ -f "$WORKAROUND_LOG" ]; then
            echo "Privilege Escalation Audit Log:"
            echo "════════════════════════════════"
            cat "$WORKAROUND_LOG"
        else
            echo "No audit log entries found"
        fi
        ;;
    --platform-info)
        echo "Platform: $(get_platform)"
        echo "Privilege Escalator: $(get_privilege_escalator)"
        echo "Elevated: $(is_elevated && echo 'Yes' || echo 'No')"
        echo "User: $USER"
        ;;
    --test-escalation)
        echo "Testing privilege escalation..."
        execute_with_privileges "echo 'Success: Running with elevated privileges'" "Test Escalation" "low"
        ;;
    --help|help|-h)
        show_usage
        ;;
    *)
        log_error "No operation specified"
        echo
        show_usage
        exit 1
        ;;
esac
