#!/usr/bin/env bash
# BLUX Guard Modules Update
# Updates blux_modules and pulls latest security & sensor code
# Cross-platform compatible: Linux, macOS, Windows (Git Bash), Termux
# Version: 1.0.0
# Author: Outer Void Team

set -euo pipefail  # Exit on error, undefined variables, pipe failures
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"

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
    if [ "$(uname)" = "Linux" ] || [ "$(uname)" = "Darwin" ]; then
        [ "$(id -u)" -eq 0 ]
    elif [ "$(uname)" = "Android" ]; then  # Termux
        [ "$(id -u)" -eq 0 ]
    else  # Windows (Git Bash/Cygwin)
        # Check if running as administrator in Windows
        net session >/dev/null 2>&1
        return $?
    fi
}

# Platform-specific path handling
get_backup_dir() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    if [ "$(uname)" = "Darwin" ]; then
        echo "$BLUX_ROOT/backups/backup_${timestamp}"
    elif [ "$(uname)" = "Android" ]; then
        echo "/data/data/com.termux/files/home/blux_backups/backup_${timestamp}"
    else
        echo "$BLUX_ROOT/backups/backup_${timestamp}"
    fi
}

# Dependency check function
check_dependencies() {
    local missing_deps=()
    
    # Check for essential commands
    for cmd in python3 git; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        
        # Platform-specific installation hints
        case "$(uname)" in
            "Linux")
                if command -v apt >/dev/null 2>&1; then
                    log_info "Install with: sudo apt update && sudo apt install ${missing_deps[*]}"
                elif command -v yum >/dev/null 2>&1; then
                    log_info "Install with: sudo yum install ${missing_deps[*]}"
                elif command -v pacman >/dev/null 2>&1; then
                    log_info "Install with: sudo pacman -S ${missing_deps[*]}"
                fi
                ;;
            "Darwin")
                if command -v brew >/dev/null 2>&1; then
                    log_info "Install with: brew install ${missing_deps[*]}"
                else
                    log_info "Install from: https://www.python.org/downloads/"
                fi
                ;;
            "Android")  # Termux
                log_info "Install with: pkg install ${missing_deps[*]}"
                ;;
        esac
        return 1
    fi
    return 0
}

# Security validation function
validate_environment() {
    log_info "Validating environment security..."
    
    # Check if we're in a safe directory
    if [ ! -f "$BLUX_ROOT/blux_modules/__init__.py" ]; then
        log_error "BLUX root directory not found or invalid"
        return 1
    fi
    
    # Check write permissions
    if [ ! -w "$BLUX_ROOT" ]; then
        log_error "No write permission to BLUX root directory"
        if is_root; then
            log_warning "Running as root - consider user-space installation for security"
        fi
        return 1
    fi
    
    # Verify config directory permissions
    if [ -d "$CONFIG_DIR" ]; then
        if [ "$(uname)" != "Windows" ] && [ -n "$(find "$CONFIG_DIR" -name "*.hash" -perm /o+r 2>/dev/null)" ]; then
            log_warning "Insecure permissions detected on config files"
            log_info "Fixing permissions..."
            find "$CONFIG_DIR" -name "*.hash" -exec chmod 600 {} \; 2>/dev/null || true
        fi
    fi
    
    return 0
}

# Backup function with rollback capability
create_backup() {
    local backup_dir
    backup_dir=$(get_backup_dir)
    
    log_info "Creating backup in: $backup_dir"
    
    if ! mkdir -p "$backup_dir"; then
        log_error "Failed to create backup directory"
        return 1
    fi
    
    # Backup critical components
    local backup_items=(
        "blux_modules"
        "rules"
        "config"
        "requirements.txt"
        "initiate_cockpit.py"
    )
    
    for item in "${backup_items[@]}"; do
        if [ -e "$BLUX_ROOT/$item" ]; then
            cp -r "$BLUX_ROOT/$item" "$backup_dir/" 2>/dev/null || 
            log_warning "Could not backup: $item"
        fi
    done
    
    # Create backup manifest
    cat > "$backup_dir/backup_manifest.txt" << EOF
BLUX Guard Backup
Created: $(date)
Version: 2.0.0
Backup ID: $(basename "$backup_dir")
Contents: ${backup_items[*]}
EOF
    
    echo "$backup_dir"  # Return backup directory path
}

# Git update with fallbacks
update_from_git() {
    if [ -d "$BLUX_ROOT/.git" ]; then
        log_info "Updating from Git repository..."
        
        # Check if we have network connectivity
        if ! git ls-remote origin >/dev/null 2>&1; then
            log_warning "No network connectivity or Git remote unavailable"
            return 1
        fi
        
        # Stash local changes if any
        if git status --porcelain | grep -q .; then
            log_info "Stashing local changes..."
            git stash push -m "BLUX update $(date +%Y%m%d_%H%M%S)"
        fi
        
        # Pull updates
        if git pull --rebase origin main; then
            log_success "Git update completed"
            return 0
        else
            log_error "Git update failed"
            # Restore stashed changes on failure
            if git stash list | grep -q "BLUX update"; then
                git stash pop || log_warning "Could not restore stashed changes"
            fi
            return 1
        fi
    else
        log_warning "Manual installation detected - skipping Git update"
        return 1
    fi
}

# Dependency management with fallbacks
update_dependencies() {
    log_info "Updating Python dependencies..."
    
    # Check for virtual environment
    local venv_dir="${BLUX_ROOT}/venv"
    local python_cmd="python3"
    local pip_cmd="pip"
    
    if [ -f "${venv_dir}/bin/activate" ]; then
        log_info "Using virtual environment"
        source "${venv_dir}/bin/activate"
        python_cmd="${venv_dir}/bin/python"
        pip_cmd="${venv_dir}/bin/pip"
    elif [ "$(uname)" = "Windows" ]; then
        # Windows-specific virtual environment path
        if [ -f "${venv_dir}/Scripts/activate" ]; then
            source "${venv_dir}/Scripts/activate"
            python_cmd="${venv_dir}/Scripts/python"
            pip_cmd="${venv_dir}/Scripts/pip"
        fi
    fi
    
    # Upgrade pip first
    if ! $pip_cmd install --upgrade pip; then
        log_warning "pip upgrade failed - continuing with existing version"
    fi
    
    # Install/upgrade requirements
    if [ -f "$BLUX_ROOT/requirements.txt" ]; then
        if $pip_cmd install -r "$BLUX_ROOT/requirements.txt" --upgrade; then
            log_success "Dependencies updated successfully"
        else
            log_error "Failed to update some dependencies"
            log_info "Attempting individual package installation..."
            
            # Fallback: install packages individually
            while IFS= read -r package; do
                [ -z "$package" ] && continue
                [[ "$package" =~ ^# ]] && continue
                
                if $pip_cmd install "$package" --upgrade; then
                    log_success "Installed: $package"
                else
                    log_warning "Failed to install: $package"
                fi
            done < "$BLUX_ROOT/requirements.txt"
        fi
    else
        log_warning "requirements.txt not found - installing core dependencies"
        
        # Core dependencies fallback
        local core_packages=(
            "argon2-cffi>=21.3.0"
            "cryptography>=3.4.8"
            "psutil>=5.9.0"
            "rich>=13.0.0"
        )
        
        for package in "${core_packages[@]}"; do
            if $pip_cmd install "$package"; then
                log_success "Installed: $package"
            else
                log_error "Failed to install core package: $package"
            fi
        done
    fi
}

# Module integrity verification
verify_modules() {
    log_info "Verifying module integrity..."
    
    local verification_script=$(cat << 'PYTHON_EOF'
import sys
import importlib
import traceback
from pathlib import Path

def verify_module(module_name, class_name=None):
    """Verify a specific module can be imported and instantiated"""
    try:
        module = importlib.import_module(f"blux_modules.{module_name}")
        print(f"✓ {module_name}: Import successful")
        
        if class_name and hasattr(module, class_name):
            cls = getattr(module, class_name)
            # Try to instantiate if no required parameters
            try:
                instance = cls()
                if hasattr(instance, 'get_status'):
                    status = instance.get_status()
                    print(f"  ✓ {class_name}: Instantiation successful")
                else:
                    print(f"  ✓ {class_name}: Instantiation successful (no status method)")
            except TypeError as e:
                if "required positional argument" in str(e):
                    print(f"  ✓ {class_name}: Class requires parameters (normal)")
                else:
                    raise
            except Exception as e:
                print(f"  ⚠ {class_name}: Instantiation warning: {e}")
        
        return True
    except Exception as e:
        print(f"✗ {module_name}: FAILED - {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()
        return False

# Verify core modules
modules_to_check = [
    ("security_engine", "SecurityEngine"),
    ("sensor_manager", "SensorManager"),
    ("decision_engine", "DecisionEngine"),
    ("anti_tamper", "AntiTamper")
]

all_ok = True
for module_name, class_name in modules_to_check:
    if not verify_module(module_name, class_name):
        all_ok = False

# Check for essential files
essential_files = [
    "rules/rules.json",
    "config/auth.json",
    "requirements.txt"
]

for file_path in essential_files:
    if Path(file_path).exists():
        print(f"✓ Config: {file_path} exists")
    else:
        print(f"⚠ Config: {file_path} missing")
        all_ok = False

sys.exit(0 if all_ok else 1)
PYTHON_EOF
)

    if ! python3 -c "$verification_script" "$@"; then
        log_error "Module verification failed"
        return 1
    fi
    
    log_success "All modules verified successfully"
    return 0
}

# Rollback function
rollback_update() {
    local backup_dir="$1"
    local reason="$2"
    
    log_error "Update failed: $reason"
    log_info "Attempting rollback from backup: $backup_dir"
    
    if [ -d "$backup_dir" ]; then
        # Restore backed up items
        for item in "blux_modules" "rules" "config" "requirements.txt"; do
            if [ -e "$backup_dir/$item" ]; then
                rm -rf "$BLUX_ROOT/$item" 2>/dev/null || true
                cp -r "$backup_dir/$item" "$BLUX_ROOT/" 2>/dev/null && 
                log_success "Restored: $item" ||
                log_warning "Failed to restore: $item"
            fi
        done
        log_success "Rollback completed successfully"
    else
        log_error "Backup directory not found - manual recovery required"
    fi
}

# Cleanup function
cleanup_backups() {
    log_info "Cleaning up old backups..."
    
    local backup_parent
    if [ "$(uname)" = "Android" ]; then
        backup_parent="/data/data/com.termux/files/home/blux_backups"
    else
        backup_parent="$BLUX_ROOT/backups"
    fi
    
    if [ -d "$backup_parent" ]; then
        # Keep only last 5 backups
        find "$backup_parent" -name "backup_*" -type d | sort -r | tail -n +6 | while read -r old_backup; do
            log_info "Removing old backup: $(basename "$old_backup")"
            rm -rf "$old_backup"
        done
    fi
}

# Main update function
main() {
    echo -e "${BLUE}"
    echo "🔄 BLUX Guard System Update"
    echo "==========================="
    echo -e "${NC}"
    
    # Security and dependency checks
    if ! check_dependencies; then
        log_error "Dependency check failed"
        exit 1
    fi
    
    if ! validate_environment; then
        log_error "Environment validation failed"
        exit 1
    fi
    
    local backup_dir=""
    local update_success=true
    
    # Create backup
    if ! backup_dir=$(create_backup); then
        log_error "Backup creation failed - aborting update"
        exit 1
    fi
    
    # Update process with error handling
    if ! update_from_git; then
        log_warning "Git update failed - continuing with manual update"
    fi
    
    if ! update_dependencies; then
        log_warning "Dependency update had issues - continuing"
    fi
    
    if ! verify_modules; then
        log_error "Module verification failed"
        update_success=false
    fi
    
    # Handle update result
    if [ "$update_success" = false ]; then
        rollback_update "$backup_dir" "Module verification failed"
        exit 1
    else
        log_success "Update completed successfully"
        cleanup_backups
        
        # Final security check
        log_info "Performing final security check..."
        find "$CONFIG_DIR" -name "*.hash" -exec chmod 600 {} \; 2>/dev/null || true
        
        # Display update summary
        echo
        echo -e "${GREEN}🎉 BLUX Guard Update Complete${NC}"
        echo "══════════════════════════"
        echo "✓ Backup created: $(basename "$backup_dir")"
        echo "✓ Dependencies updated"
        echo "✓ Modules verified"
        echo "✓ Security permissions applied"
        echo
        echo "Next: Run 'python initiate_cockpit.py' to start BLUX Guard"
    fi
}

# Security check: Prevent running as root unless explicitly allowed
if is_root && [ "${BLUX_ALLOW_ROOT_UPDATE:-0}" -ne 1 ]; then
    log_warning "Running as root user - this is not recommended for security"
    log_info "To allow root updates, set: BLUX_ALLOW_ROOT_UPDATE=1"
    log_info "Falling back to user privileges..."
    
    # Drop privileges if possible
    if [ -n "${SUDO_USER:-}" ]; then
        exec sudo -u "$SUDO_USER" "$0" "$@"
    elif [ -n "${USER:-}" ]; then
        exec runuser -u "$USER" -- "$0" "$@"
    else
        log_error "Cannot drop root privileges - continuing with warning"
    fi
fi

# Handle script arguments
case "${1:-}" in
    "--verify-only")
        verify_modules "${@:2}"
        ;;
    "--rollback")
        if [ -n "${2:-}" ] && [ -d "$BLUX_ROOT/backups/$2" ]; then
            rollback_update "$BLUX_ROOT/backups/$2" "Manual rollback requested"
        else
            log_error "Specify valid backup directory for rollback"
            log_info "Available backups:"
            find "$BLUX_ROOT/backups" -name "backup_*" -type d 2>/dev/null | sort -r | head -5
        fi
        ;;
    "--help" | "-h")
        echo "BLUX Guard Update Script"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --verify-only    Verify module integrity without updating"
        echo "  --rollback DIR   Rollback to specified backup directory"
        echo "  --help, -h       Show this help message"
        echo
        echo "Environment variables:"
        echo "  BLUX_ALLOW_ROOT_UPDATE=1  Allow running as root"
        echo "  BLUX_CONFIG_DIR=PATH      Custom config directory"
        ;;
    *)
        main "$@"
        ;;
esac
