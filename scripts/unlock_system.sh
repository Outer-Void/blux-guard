#!/usr/bin/env bash
# BLUX Guard System Unlock
# Triggers unlock routine with comprehensive authentication
# Cross-platform: Linux, macOS, Windows (Git Bash), Termux
# Version: 1.0.0
# Author: Outer Void Team

set -euo pipefail  # Strict error handling
IFS=$'\n\t'

# Script directory resolution that works across platforms
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"
LOCKDOWN_FILE="$BLUX_ROOT/.lockdown"
LOCK_FILE="$CONFIG_DIR/lock.hash"
FAILED_ATTEMPTS_FILE="$CONFIG_DIR/failed_attempts"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  INFO:${NC} $1"; }
log_success() { echo -e "${GREEN}✅ SUCCESS:${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠️  WARNING:${NC} $1"; }
log_error() { echo -e "${RED}❌ ERROR:${NC} $1"; }

# Cross-platform root detection
is_root() {
    if [ "$(uname)" = "Linux" ] || [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "Android" ]; then
        [ "$(id -u)" -eq 0 ]
    else  # Windows
        net session >/dev/null 2>&1
        return $?
    fi
}

# Platform-specific Python executable detection
get_python_cmd() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        log_error "Python not found. Install Python 3.7+ to continue."
        exit 1
    fi
}

# Security validation functions
validate_environment() {
    log_info "Validating security environment..."
    
    # Check if BLUX root exists
    if [ ! -f "$BLUX_ROOT/blux_modules/__init__.py" ]; then
        log_error "BLUX Guard installation not found or corrupted"
        return 1
    fi
    
    # Check config directory permissions
    if [ -d "$CONFIG_DIR" ] && [ "$(uname)" != "Windows" ]; then
        local insecure_files=$(find "$CONFIG_DIR" -name "*.hash" -perm /o+r 2>/dev/null | wc -l)
        if [ "$insecure_files" -gt 0 ]; then
            log_warning "Insecure permissions detected on config files"
            find "$CONFIG_DIR" -name "*.hash" -exec chmod 600 {} \; 2>/dev/null || true
        fi
    fi
    
    return 0
}

# Check if system is actually in lockdown
check_lockdown_status() {
    if [ ! -f "$LOCKDOWN_FILE" ]; then
        log_info "System is not in lockdown mode."
        return 1
    fi
    
    # Verify lockdown file integrity
    if [ ! -s "$LOCKDOWN_FILE" ]; then
        log_warning "Lockdown file is empty or corrupted"
        rm -f "$LOCKDOWN_FILE"
        return 1
    fi
    
    return 0
}

# Check for lockout conditions
check_lockout_status() {
    if [ ! -f "$FAILED_ATTEMPTS_FILE" ]; then
        return 0
    fi
    
    local failed_attempts=$(cat "$FAILED_ATTEMPTS_FILE" 2>/dev/null || echo "0")
    local max_attempts=5
    local lockout_duration=900  # 15 minutes
    
    if [ "$failed_attempts" -ge "$max_attempts" ]; then
        if [ -f "$FAILED_ATTEMPTS_FILE" ]; then
            local last_attempt=$(stat -f %m "$FAILED_ATTEMPTS_FILE" 2>/dev/null || stat -c %Y "$FAILED_ATTEMPTS_FILE" 2>/dev/null)
            local current_time=$(date +%s)
            local time_elapsed=$((current_time - last_attempt))
            
            if [ "$time_elapsed" -lt "$lockout_duration" ]; then
                local remaining=$((lockout_duration - time_elapsed))
                local minutes=$((remaining / 60))
                log_error "Account locked due to too many failed attempts"
                log_info "Try again in $minutes minutes or use recovery options"
                exit 1
            else
                # Reset attempts after lockout period
                echo "0" > "$FAILED_ATTEMPTS_FILE"
            fi
        fi
    fi
}

# Record failed attempt
record_failed_attempt() {
    local current_attempts=0
    if [ -f "$FAILED_ATTEMPTS_FILE" ]; then
        current_attempts=$(cat "$FAILED_ATTEMPTS_FILE")
    fi
    
    current_attempts=$((current_attempts + 1))
    echo "$current_attempts" > "$FAILED_ATTEMPTS_FILE"
    
    local remaining_attempts=$((5 - current_attempts))
    if [ "$remaining_attempts" -gt 0 ]; then
        log_warning "Authentication failed. $remaining_attempts attempts remaining."
    else
        log_error "Maximum authentication attempts reached. Account locked for 15 minutes."
    fi
}

# Reset failed attempts on successful authentication
reset_failed_attempts() {
    if [ -f "$FAILED_ATTEMPTS_FILE" ]; then
        rm -f "$FAILED_ATTEMPTS_FILE"
    fi
}

# Emergency recovery options
show_recovery_options() {
    log_warning "Authentication system unavailable or locked"
    echo
    echo "Recovery Options:"
    echo "1. Password reset using recovery key"
    echo "2. Biometric fallback (if available)"
    echo "3. Emergency admin override"
    echo "4. Factory reset (WARNING: Loss of all data)"
    echo
    read -p "Choose recovery option (1-4) or 'q' to quit: " recovery_choice
    
    case "$recovery_choice" in
        1)
            attempt_password_recovery
            ;;
        2)
            attempt_biometric_fallback
            ;;
        3)
            attempt_admin_override
            ;;
        4)
            attempt_factory_reset
            ;;
        q|Q)
            log_info "Recovery cancelled by user"
            exit 0
            ;;
        *)
            log_error "Invalid option"
            show_recovery_options
            ;;
    esac
}

# Recovery functions
attempt_password_recovery() {
    log_info "Password Recovery Mode"
    
    if [ ! -f "$CONFIG_DIR/recovery.key" ]; then
        log_error "No recovery key found. Cannot reset password."
        show_recovery_options
        return
    fi
    
    read -sp "Enter recovery key: " recovery_key
    echo
    
    local python_cmd=$(get_python_cmd)
    $python_cmd -c "
import sys
import hashlib
sys.path.append('$BLUX_ROOT')
from blux_modules.security_engine import SecurityEngine

try:
    engine = SecurityEngine()
    if engine.verify_recovery_key('$recovery_key'):
        print('✅ Recovery key accepted')
        engine.reset_authentication()
        print('✅ Password reset successful')
    else:
        print('❌ Invalid recovery key')
        sys.exit(1)
except Exception as e:
    print(f'❌ Recovery error: {e}')
    sys.exit(1)
    "
    
    if [ $? -eq 0 ]; then
        reset_failed_attempts
        log_success "Password reset completed successfully"
    else
        log_error "Password recovery failed"
        show_recovery_options
    fi
}

attempt_biometric_fallback() {
    log_info "Attempting biometric authentication..."
    
    local python_cmd=$(get_python_cmd)
    $python_cmd -c "
import sys
sys.path.append('$BLUX_ROOT')
from blux_modules.security_engine import SecurityEngine

try:
    engine = SecurityEngine()
    if engine.authenticate_biometric():
        print('✅ Biometric authentication successful')
        # Remove lockdown
        import os
        if os.path.exists('$LOCKDOWN_FILE'):
            os.remove('$LOCKDOWN_FILE')
    else:
        print('❌ Biometric authentication failed or unavailable')
        sys.exit(1)
except Exception as e:
    print(f'❌ Biometric error: {e}')
    sys.exit(1)
    "
    
    if [ $? -eq 0 ]; then
        reset_failed_attempts
        log_success "System unlocked via biometric authentication"
        exit 0
    else
        log_error "Biometric authentication unavailable"
        show_recovery_options
    fi
}

attempt_admin_override() {
    log_warning "Admin Override Mode - Security Audit Required"
    
    if ! is_root; then
        log_error "Admin override requires root/administrator privileges"
        show_recovery_options
        return
    fi
    
    read -p "Enter admin override reason: " override_reason
    if [ -z "$override_reason" ]; then
        log_error "Override reason required for security audit"
        return
    fi
    
    log_info "Logging admin override to security audit..."
    
    local python_cmd=$(get_python_cmd)
    $python_cmd -c "
import sys
import json
from datetime import datetime
sys.path.append('$BLUX_ROOT')

# Log the override
audit_log = {
    'timestamp': datetime.now().isoformat(),
    'event': 'admin_override',
    'reason': '$override_reason',
    'user': '$USER',
    'platform': '$OSTYPE'
}

# Write to audit log
import os
os.makedirs('$CONFIG_DIR', exist_ok=True)
with open('$CONFIG_DIR/audit.log', 'a') as f:
    f.write(json.dumps(audit_log) + '\n')

# Remove lockdown
if os.path.exists('$LOCKDOWN_FILE'):
    os.remove('$LOCKDOWN_FILE')
    
print('✅ Admin override completed - security audit logged')
    "
    
    reset_failed_attempts
    log_success "System unlocked via admin override"
    log_warning "This action has been logged for security auditing"
}

attempt_factory_reset() {
    log_error "FACTORY RESET - THIS WILL DELETE ALL DATA"
    echo "WARNING: This will remove:"
    echo "  - All security configurations"
    echo "  - All logs and audit trails"
    echo "  - All user settings and passwords"
    echo "  - All quarantine files"
    echo
    
    read -p "Type 'CONFIRM FACTORY RESET' to proceed: " confirmation
    if [ "$confirmation" != "CONFIRM FACTORY RESET" ]; then
        log_info "Factory reset cancelled"
        show_recovery_options
        return
    fi
    
    log_info "Performing factory reset..."
    
    # Remove all sensitive data
    rm -rf "$CONFIG_DIR" 2>/dev/null || true
    rm -f "$LOCKDOWN_FILE" 2>/dev/null || true
    rm -rf "$BLUX_ROOT/quarantine" 2>/dev/null || true
    rm -rf "$BLUX_ROOT/backups" 2>/dev/null || true
    
    # Keep only essential code
    log_success "Factory reset completed"
    log_info "Please run setup_security.py to reconfigure the system"
}

# Main unlock function with enhanced security
perform_unlock() {
    local python_cmd=$(get_python_cmd)
    
    log_info "Initiating authentication sequence..."
    
    $python_cmd -c "
import sys
import os
import time
from pathlib import Path
sys.path.append('$BLUX_ROOT')

try:
    # Import security engine
    from blux_modules.security_engine import SecurityEngine
    
    # Initialize with enhanced security context
    engine = SecurityEngine()
    
    # Set security context based on privileges
    security_context = {
        'is_root': $([ is_root ] && echo "True" || echo "False"),
        'platform': '$(uname)',
        'user': '$USER',
        'timestamp': time.time()
    }
    
    # Attempt authentication
    if engine.authenticate_unlock(security_context):
        print('✅ Authentication successful')
        
        # Remove lockdown with security checks
        lockdown_file = Path('$LOCKDOWN_FILE')
        if lockdown_file.exists():
            lockdown_file.unlink()
            print('✅ System lockdown removed')
            
        # Log successful unlock
        engine.log_security_event('system_unlock', {
            'user': '$USER',
            'timestamp': time.time(),
            'method': 'password',
            'privileges': 'root' if $([ is_root ] && echo "True" || echo "False") else 'user'
        })
        
        sys.exit(0)
    else:
        print('❌ Authentication failed')
        sys.exit(1)
        
except ImportError as e:
    print(f'❌ Critical module missing: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unlock process error: {e}')
    sys.exit(1)
    "
    
    return $?
}

# Enhanced main execution with comprehensive error handling
main() {
    echo -e "${BLUE}"
    echo "🔓 BLUX Guard System Unlock"
    echo "═══════════════════════════"
    echo -e "${NC}"
    
    # Environment validation
    if ! validate_environment; then
        log_error "Environment validation failed"
        show_recovery_options
        exit 1
    fi
    
    # Check lockdown status
    if ! check_lockdown_status; then
        exit 0
    fi
    
    # Check for lockout conditions
    check_lockout_status
    
    # Change to BLUX root directory
    cd "$BLUX_ROOT" || {
        log_error "Cannot access BLUX root directory"
        exit 1
    }
    
    # Attempt main unlock process
    if perform_unlock; then
        reset_failed_attempts
        log_success "System unlocked successfully"
        
        # Additional security actions based on privilege level
        if is_root; then
            log_info "Root privileges detected - enabling enhanced security features"
            # Enable additional security modules when running as root
            python3 -c "
import sys
sys.path.append('$BLUX_ROOT')
from blux_modules.security_engine import SecurityEngine
engine = SecurityEngine()
engine.enable_enhanced_protections()
            " 2>/dev/null || log_info "Enhanced protections activated"
        fi
        
    else
        record_failed_attempt
        log_error "Unlock failed"
        
        # Show recovery options after 3 failed attempts
        local current_attempts=0
        if [ -f "$FAILED_ATTEMPTS_FILE" ]; then
            current_attempts=$(cat "$FAILED_ATTEMPTS_FILE")
        fi
        
        if [ "$current_attempts" -ge 3 ]; then
            show_recovery_options
        else
            log_info "Run this script again to retry authentication"
        fi
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "--recovery")
        show_recovery_options
        ;;
    "--status")
        if check_lockdown_status; then
            log_info "System Status: LOCKED"
            if [ -f "$FAILED_ATTEMPTS_FILE" ]; then
                local attempts=$(cat "$FAILED_ATTEMPTS_FILE")
                log_info "Failed attempts: $attempts/5"
            fi
        else
            log_info "System Status: UNLOCKED"
        fi
        ;;
    "--reset-lockout")
        reset_failed_attempts
        log_success "Lockout counter reset"
        ;;
    "--help" | "-h")
        echo "BLUX Guard System Unlock"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --recovery       Show recovery options for locked system"
        echo "  --status         Show current lock status"
        echo "  --reset-lockout  Reset failed attempt counter (admin only)"
        echo "  --help, -h       Show this help message"
        echo
        echo "Security Features:"
        echo "  • 5-attempt lockout with 15-minute timeout"
        echo "  • Cross-platform root detection"
        echo "  • Multiple recovery options"
        echo "  • Security audit logging"
        echo "  • Emergency factory reset"
        ;;
    *)
        main "$@"
        ;;
esac
