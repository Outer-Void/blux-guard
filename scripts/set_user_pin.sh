#!/bin/bash
# BLUX Guard User PIN Setup
# Prompts user to set screen pin or device password for lockdown
# Cross-platform: Linux, macOS, Windows (Git Bash), Termux
# Version: 1.0.0
# Author: Outer Void Team

set -euo pipefail  # Strict error handling

# Script directory resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"
AUTH_CONFIG="$BLUX_ROOT/config/auth.json"
LOCK_FILE="$CONFIG_DIR/lock.hash"
RECOVERY_KEY_FILE="$CONFIG_DIR/recovery.key"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  INFO:${NC} $1"; }
log_success() { echo -e "${GREEN}✅ SUCCESS:${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠️  WARNING:${NC} $1"; }
log_error() { echo -e "${RED}❌ ERROR:${NC} $1"; }
log_debug() { echo -e "${CYAN}🐛 DEBUG:${NC} $1"; }

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
        # Verify it's Python 3
        if python -c "import sys; sys.exit(0) if sys.version_info >= (3, 7) else sys.exit(1)"; then
            echo "python"
        else
            log_error "Python 3.7+ required but not found"
            exit 1
        fi
    else
        log_error "Python not found. Install Python 3.7+ to continue."
        exit 1
    fi
}

# Dependency validation
validate_dependencies() {
    log_info "Validating system dependencies..."
    
    local python_cmd=$(get_python_cmd)
    
    # Check for required Python packages
    if ! $python_cmd -c "import argon2, cryptography, json, getpass, secrets, hashlib" 2>/dev/null; then
        log_warning "Missing some Python dependencies"
        
        # Attempt to install missing dependencies
        log_info "Attempting to install required packages..."
        if $python_cmd -m pip install --user argon2-cffi cryptography 2>/dev/null; then
            log_success "Dependencies installed successfully"
        else
            log_error "Failed to install required dependencies"
            log_info "Please run: pip install argon2-cffi cryptography"
            return 1
        fi
    fi
    
    return 0
}

# Environment validation
validate_environment() {
    log_info "Validating environment..."
    
    # Check BLUX root structure
    if [ ! -f "$BLUX_ROOT/blux_modules/__init__.py" ]; then
        log_error "BLUX Guard installation not found or corrupted"
        log_info "Expected BLUX root at: $BLUX_ROOT"
        return 1
    fi
    
    # Check if config directory exists or create it
    if [ ! -d "$CONFIG_DIR" ]; then
        log_info "Creating config directory: $CONFIG_DIR"
        if ! mkdir -p "$CONFIG_DIR"; then
            log_error "Failed to create config directory"
            return 1
        fi
    fi
    
    # Set secure permissions on config directory
    if [ "$(uname)" != "Windows" ]; then
        chmod 700 "$CONFIG_DIR" 2>/dev/null || log_warning "Could not set permissions on config directory"
    fi
    
    return 0
}

# Auth config validation and creation
setup_auth_config() {
    if [ ! -f "$AUTH_CONFIG" ]; then
        log_warning "Auth config not found - creating default configuration"
        
        local python_cmd=$(get_python_cmd)
        $python_cmd -c "
import json
import os
from pathlib import Path

# Create default auth configuration
auth_config = {
    'version': '2.0.0',
    'auth_method': 'pin',
    'max_attempts': 5,
    'lockout_duration': 900,
    'pin_length': {
        'min': 4,
        'max': 12,
        'allow_letters': True,
        'allow_special': False
    },
    'require_auth_for': [
        'lockdown',
        'config_changes', 
        'sensor_disable',
        'quarantine_access',
        'log_deletion'
    ],
    'pin_set': False,
    'recovery_enabled': True,
    'biometric_fallback': False,
    'security_level': 'standard'
}

# Create config directory if needed
Path('config').mkdir(exist_ok=True)

# Write auth config
with open('$AUTH_CONFIG', 'w') as f:
    json.dump(auth_config, f, indent=2)

print('✅ Default auth configuration created')
        " || {
            log_error "Failed to create auth configuration"
            return 1
        }
    fi
    
    # Validate auth config structure
    if ! python3 -c "
import json
try:
    with open('$AUTH_CONFIG') as f:
        config = json.load(f)
    required_fields = ['auth_method', 'max_attempts', 'pin_set']
    if all(field in config for field in required_fields):
        print('VALID')
    else:
        print('INVALID')
except Exception as e:
    print(f'ERROR: {e}')
" | grep -q "VALID"; then
        log_error "Auth configuration is invalid or corrupted"
        return 1
    fi
    
    return 0
}

# Generate secure recovery key
generate_recovery_key() {
    local python_cmd=$(get_python_cmd)
    
    $python_cmd -c "
import secrets
import hashlib
import json
from pathlib import Path

# Generate cryptographically secure recovery key
recovery_key = secrets.token_urlsafe(32)
key_hash = hashlib.sha256(recovery_key.encode()).hexdigest()

# Store only the hash for verification
recovery_data = {
    'key_hash': key_hash,
    'created': '$(date -Iseconds)',
    'used': False
}

# Save recovery data
Path('$CONFIG_DIR').mkdir(parents=True, exist_ok=True)
with open('$RECOVERY_KEY_FILE', 'w') as f:
    json.dump(recovery_data, f, indent=2)

# Set secure permissions
import os
if os.name != 'nt':  # Not Windows
    os.chmod('$RECOVERY_KEY_FILE', 0o600)

print('RECOVERY_KEY:' + recovery_key)
    "
}

# Enhanced PIN validation
validate_pin_strength() {
    local pin="$1"
    local python_cmd=$(get_python_cmd)
    
    $python_cmd -c "
import sys
import json

def validate_pin_strength(pin, config_path):
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        pin_config = config.get('pin_length', {})
        min_len = pin_config.get('min', 4)
        max_len = pin_config.get('max', 12)
        allow_letters = pin_config.get('allow_letters', True)
        allow_special = pin_config.get('allow_special', False)
        
        # Length check
        if len(pin) < min_len:
            return f'PIN too short. Minimum {min_len} characters required.'
        
        if len(pin) > max_len:
            return f'PIN too long. Maximum {max_len} characters allowed.'
        
        # Character set validation
        if not allow_letters and any(c.isalpha() for c in pin):
            return 'Letters are not allowed in PIN.'
        
        if not allow_special and any(not c.isalnum() for c in pin):
            return 'Special characters are not allowed in PIN.'
        
        # Common PIN check (basic)
        common_pins = ['1234', '0000', '1111', '9999']
        if pin in common_pins:
            return 'PIN is too common. Choose a more secure PIN.'
        
        return None
        
    except Exception as e:
        return f'Validation error: {e}'

pin = '$pin'
config_path = '$AUTH_CONFIG'
error = validate_pin_strength(pin, config_path)

if error:
    print(f'VALIDATION_ERROR:{error}')
    sys.exit(1)
else:
    print('VALID')
    sys.exit(0)
    "
}

# Main PIN setup function with enhanced security
setup_pin() {
    local python_cmd=$(get_python_cmd)
    
    log_info "Starting secure PIN setup process..."
    
    $python_cmd -c "
import sys
import json
import getpass
import secrets
import hashlib
from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerifyMismatchError

class BLUXPinManager:
    def __init__(self):
        self.config_dir = Path('$CONFIG_DIR')
        self.lock_file = self.config_dir / 'lock.hash'
        self.auth_config = Path('$AUTH_CONFIG')
        self.recovery_file = self.config_dir / 'recovery.key'
        self.ph = PasswordHasher()
        
    def load_auth_config(self):
        \"\"\"Load and validate authentication configuration\"\"\"
        try:
            with open(self.auth_config) as f:
                return json.load(f)
        except Exception as e:
            print(f'❌ Failed to load auth config: {e}')
            sys.exit(1)
    
    def save_auth_config(self, config):
        \"\"\"Save authentication configuration with backup\"\"\"
        try:
            # Create backup of existing config
            if self.auth_config.exists():
                backup_path = self.auth_config.with_suffix('.backup')
                self.auth_config.rename(backup_path)
            
            with open(self.auth_config, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
                
            return True
        except Exception as e:
            print(f'❌ Failed to save auth config: {e}')
            # Attempt to restore backup
            if 'backup_path' in locals() and backup_path.exists():
                backup_path.rename(self.auth_config)
            return False
    
    def setup_secure_environment(self):
        \"\"\"Create secure directory structure with proper permissions\"\"\"
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Set secure permissions on Unix-like systems
            if hasattr(self.config_dir, 'chmod'):
                self.config_dir.chmod(0o700)
                
            return True
        except Exception as e:
            print(f'❌ Failed to create secure environment: {e}')
            return False
    
    def generate_recovery_key(self):
        \"\"\"Generate and display a secure recovery key\"\"\"
        try:
            recovery_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(recovery_key.encode()).hexdigest()
            
            recovery_data = {
                'key_hash': key_hash,
                'created': '$(date -Iseconds)',
                'used': False
            }
            
            with open(self.recovery_file, 'w') as f:
                json.dump(recovery_data, f, indent=2)
            
            # Secure file permissions
            if hasattr(self.recovery_file, 'chmod'):
                self.recovery_file.chmod(0o600)
                
            return recovery_key
        except Exception as e:
            print(f'❌ Failed to generate recovery key: {e}')
            return None
    
    def set_pin(self, pin):
        \"\"\"Securely set the user PIN\"\"\"
        try:
            # Hash the PIN with Argon2
            pin_hash = self.ph.hash(pin)
            
            # Write hash to secure lock file
            with open(self.lock_file, 'w') as f:
                f.write(pin_hash)
            
            # Set secure permissions
            if hasattr(self.lock_file, 'chmod'):
                self.lock_file.chmod(0o600)
            
            # Update auth configuration
            config = self.load_auth_config()
            config.update({
                'pin_set': True,
                'last_modified': '$(date -Iseconds)',
                'hash_algorithm': 'argon2',
                'security_level': 'enhanced'
            })
            
            if self.save_auth_config(config):
                return True
            else:
                # Rollback PIN setting if config save fails
                self.lock_file.unlink(missing_ok=True)
                return False
                
        except HashingError as e:
            print(f'❌ Password hashing failed: {e}')
            return False
        except Exception as e:
            print(f'❌ Failed to set PIN: {e}')
            return False

def main():
    manager = BLUXPinManager()
    
    print('\\\\n🔐 BLUX Guard Enhanced PIN Setup')
    print('══════════════════════════════')
    print('This PIN will be used for:')
    print('  • System lockdown/unlock')
    print('  • Sensitive configuration changes')
    print('  • Security module access')
    print('  • Quarantine operations')
    print()
    
    # Setup secure environment
    if not manager.setup_secure_environment():
        sys.exit(1)
    
    # Load current configuration
    config = manager.load_auth_config()
    pin_config = config.get('pin_length', {})
    
    print(f'PIN Requirements:')
    print(f'  • Length: {pin_config.get(\"min\", 4)}-{pin_config.get(\"max\", 12)} characters')
    print(f'  • Letters: {\"Allowed\" if pin_config.get(\"allow_letters\", True) else \"Not allowed\"}')
    print(f'  • Special chars: {\"Allowed\" if pin_config.get(\"allow_special\", False) else \"Not allowed\"}')
    print()
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Get PIN with confirmation
            pin1 = getpass.getpass('Enter new PIN: ')
            pin2 = getpass.getpass('Confirm PIN: ')
            
            # Validate PINs match
            if pin1 != pin2:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f'❌ PINs do not match. {remaining} attempts remaining.\\\\n')
                else:
                    print('❌ Maximum attempts reached. Please run the setup again.')
                    sys.exit(1)
                continue
            
            # Validate PIN strength
            if len(pin1) < pin_config.get('min', 4):
                print(f'❌ PIN must be at least {pin_config.get(\"min\", 4)} characters\\\\n')
                continue
                
            if len(pin1) > pin_config.get('max', 12):
                print(f'❌ PIN cannot exceed {pin_config.get(\"max\", 12)} characters\\\\n')
                continue
            
            # Set the PIN
            if manager.set_pin(pin1):
                print('\\\\n✅ PIN set successfully!')
                
                # Generate and display recovery key
                print('\\\\n📋 GENERATING RECOVERY KEY...')
                recovery_key = manager.generate_recovery_key()
                if recovery_key:
                    print('\\\\n⚠️  IMPORTANT: Save this recovery key in a secure location!')
                    print('⚠️  You will need it if you forget your PIN!')
                    print('══════════════════════════════════════════════')
                    print(f'Recovery Key: {recovery_key}')
                    print('══════════════════════════════════════════════')
                    print('\\\\n💡 Tips:')
                    print('  • Store this key in a password manager')
                    print('  • Keep a printed copy in a secure location')
                    print('  • Do not store digitally in plain text')
                
                print('\\\\n🎉 PIN setup completed successfully!')
                break
                
        except KeyboardInterrupt:
            print('\\\\n\\\\n❌ Setup cancelled by user.')
            sys.exit(1)
        except Exception as e:
            print(f'❌ Unexpected error: {e}')
            if attempt == max_attempts - 1:
                sys.exit(1)

if __name__ == '__main__':
    main()
    " || {
        log_error "PIN setup failed"
        return 1
    }
    
    return 0
}

# Security audit function
log_security_event() {
    local event="$1"
    local details="$2"
    
    local audit_log="$CONFIG_DIR/security_audit.log"
    local timestamp=$(date -Iseconds)
    
    echo "[$timestamp] $event: $details" >> "$audit_log"
    
    # Secure audit log permissions
    if [ "$(uname)" != "Windows" ]; then
        chmod 600 "$audit_log" 2>/dev/null || true
    fi
}

# Main execution function
main() {
    echo -e "${BLUE}"
    echo "🔐 BLUX Guard Enhanced PIN Setup"
    echo "══════════════════════════════"
    echo -e "${NC}"
    
    # Security warning for root execution
    if is_root && [ "${BLUX_ALLOW_ROOT_SETUP:-0}" -ne 1 ]; then
        log_warning "Running PIN setup as root - this is not recommended"
        log_info "User-specific PINs should be set by the user who will use them"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Setup cancelled"
            exit 0
        fi
    fi
    
    # Validate environment and dependencies
    if ! validate_dependencies; then
        exit 1
    fi
    
    if ! validate_environment; then
        exit 1
    fi
    
    if ! setup_auth_config; then
        exit 1
    fi
    
    # Perform PIN setup
    if setup_pin; then
        log_success "PIN setup completed successfully"
        log_security_event "pin_setup" "User PIN configured successfully"
        
        # Display next steps
        echo
        echo -e "${GREEN}Next Steps:${NC}"
        echo "1. Your PIN is now required for sensitive operations"
        echo "2. Keep your recovery key in a secure location"
        echo "3. Test your PIN by running: ./unlock_system.sh"
        echo "4. For PIN changes, run this script again"
        
    else
        log_error "PIN setup failed"
        log_security_event "pin_setup_failed" "User PIN configuration failed"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "--reset")
        log_warning "Resetting PIN configuration..."
        rm -f "$LOCK_FILE" 2>/dev/null || true
        rm -f "$RECOVERY_KEY_FILE" 2>/dev/null || true
        log_success "PIN configuration reset. Run without --reset to set new PIN."
        ;;
    "--recovery-key")
        log_info "Generating new recovery key..."
        generate_recovery_key
        ;;
    "--validate")
        if [ -f "$LOCK_FILE" ]; then
            log_success "PIN is set and configured"
        else
            log_warning "No PIN configured"
        fi
        ;;
    "--help" | "-h")
        echo "BLUX Guard PIN Setup"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --reset         Reset existing PIN configuration"
        echo "  --recovery-key  Generate new recovery key only"
        echo "  --validate      Check if PIN is configured"
        echo "  --help, -h      Show this help message"
        echo
        echo "Security Features:"
        echo "  • Argon2 password hashing"
        echo "  • Secure recovery key generation"
        echo "  • PIN strength validation"
        echo "  • Audit logging"
        echo "  • Cross-platform compatibility"
        ;;
    *)
        main "$@"
        ;;
esac
