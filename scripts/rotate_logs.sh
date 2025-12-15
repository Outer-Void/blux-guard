#!/usr/bin/env bash
# BLUX Guard Log Rotation
# Rotates /logs subfolders for anti-tamper, decisions, sensors
# Cross-platform: Linux, macOS, Windows (Git Bash), Termux
# Version: 21.0.0
# Author: Outer Void Team

set -euo pipefail  # Strict error handling
IFS=$'\n\t'

# Script directory resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"
LOG_CONFIG="$CONFIG_DIR/log_rotation.json"
ROTATION_LOCK="$CONFIG_DIR/rotation.lock"

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

# Cross-platform root detection
is_root() {
    if [ "$(uname)" = "Linux" ] || [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "Android" ]; then
        [ "$(id -u)" -eq 0 ]
    else  # Windows
        net session >/dev/null 2>&1
        return $?
    fi
}

# Platform detection
get_platform() {
    case "$(uname -s)" in
        Linux*)
            if [ -f /system/bin/adb ] || [ -d /data/data/com.termux ]; then
                echo "termux"
            else
                echo "linux"
            fi
            ;;
        Darwin*) echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Dependency validation
validate_dependencies() {
    local platform=$(get_platform)
    local missing_tools=()
    
    # Check for essential tools
    for tool in find date; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    # Check for compression tools
    if ! command -v gzip >/dev/null 2>&1; then
        log_warning "gzip not available - log compression disabled"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing essential tools: ${missing_tools[*]}"
        case "$platform" in
            termux)
                log_info "Install with: pkg install ${missing_tools[*]}"
                ;;
            linux)
                if command -v apt >/dev/null 2>&1; then
                    log_info "Install with: sudo apt install coreutils findutils"
                fi
                ;;
        esac
        return 1
    fi
    
    return 0
}

# Create default log rotation configuration
create_default_config() {
    if [ ! -f "$LOG_CONFIG" ]; then
        log_info "Creating default log rotation configuration..."
        
        mkdir -p "$CONFIG_DIR"
        cat > "$LOG_CONFIG" << EOF
{
    "version": "2.0.0",
    "retention_days": {
        "active_logs": 7,
        "compressed_logs": 30,
        "audit_logs": 90
    },
    "compression": {
        "enabled": true,
        "method": "gzip",
        "level": 6
    },
    "log_directories": [
        "logs/anti_tamper",
        "logs/sensors", 
        "logs/decisions",
        "logs/audit",
        "logs/cron"
    ],
    "permissions": {
        "active_logs": 600,
        "compressed_logs": 600,
        "directories": 700
    },
    "max_log_size": "100M",
    "notify_on_rotation": false
}
EOF
        log_success "Default configuration created: $LOG_CONFIG"
    fi
}

# Load configuration
load_config() {
    if [ ! -f "$LOG_CONFIG" ]; then
        log_warning "Log rotation config not found - using defaults"
        echo '{
            "retention_days": {"active_logs": 7, "compressed_logs": 30},
            "compression": {"enabled": true},
            "log_directories": ["logs/anti_tamper", "logs/sensors", "logs/decisions"],
            "permissions": {"active_logs": 600, "compressed_logs": 600, "directories": 700}
        }'
        return 0
    fi
    
    # Validate JSON configuration
    if ! python3 -c "
import json, sys
try:
    with open('$LOG_CONFIG') as f:
        config = json.load(f)
    print(json.dumps(config))
except Exception as e:
    print(f'CONFIG_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
        log_error "Invalid configuration file - using defaults"
        echo '{
            "retention_days": {"active_logs": 7, "compressed_logs": 30},
            "log_directories": ["logs/anti_tamper", "logs/sensors", "logs/decisions"],
            "permissions": {"active_logs": 600, "compressed_logs": 600}
        }'
    fi
}

# Cross-platform file size check
get_file_size() {
    local file="$1"
    if [ "$(get_platform)" = "windows" ]; then
        # Windows Git Bash
        stat -c%s "$file" 2>/dev/null || echo "0"
    else
        # Unix-like systems
        stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0"
    fi
}

# Cross-platform find command with fallbacks
safe_find() {
    local directory="$1"
    local pattern="$2"
    
    if [ ! -d "$directory" ]; then
        return 1
    fi
    
    # Use find with platform-specific options
    case "$(get_platform)" in
        windows)
            find "$directory" -name "$pattern" 2>/dev/null || true
            ;;
        *)
            find "$directory" -name "$pattern" 2>/dev/null || true
            ;;
    esac
}

# Secure file operations with error handling
secure_compress() {
    local file="$1"
    local compression_enabled="${2:-true}"
    
    if [ ! -f "$file" ]; then
        return 1
    fi
    
    # Check if file is already compressed
    if [[ "$file" == *.gz ]] || [[ "$file" == *.zip ]]; then
        return 0
    fi
    
    if [ "$compression_enabled" = "true" ] && command -v gzip >/dev/null 2>&1; then
        if gzip -6 "$file" 2>/dev/null; then
            log_info "Compressed: $(basename "$file")"
            # Set secure permissions on compressed file
            chmod 600 "${file}.gz" 2>/dev/null || true
            return 0
        else
            log_warning "Failed to compress: $(basename "$file")"
            return 1
        fi
    fi
    
    return 0
}

# Secure file deletion
secure_delete() {
    local file="$1"
    local reason="$2"
    
    if [ ! -f "$file" ]; then
        return 1
    fi
    
    log_info "Removing: $(basename "$file") ($reason)"
    
    # For sensitive log files, consider secure deletion on supported platforms
    if [ "$(get_platform)" = "linux" ] && command -v shred >/dev/null 2>&1; then
        shred -u -z -n 1 "$file" 2>/dev/null && return 0
    fi
    
    # Standard deletion
    rm -f "$file" 2>/dev/null && return 0
    
    log_warning "Failed to delete: $(basename "$file")"
    return 1
}

# Rotation function with enhanced security
rotate_logs() {
    local log_dir="$1"
    local config="$2"
    
    local active_days=$(echo "$config" | python3 -c "import json, sys; print(json.load(sys.stdin)['retention_days'].get('active_logs', 7))")
    local compressed_days=$(echo "$config" | python3 -c "import json, sys; print(json.load(sys.stdin)['retention_days'].get('compressed_logs', 30))")
    local compression_enabled=$(echo "$config" | python3 -c "import json, sys; print(str(json.load(sys.stdin)['compression'].get('enabled', True)).lower())")
    local dir_permissions=$(echo "$config" | python3 -c "import json, sys; print(json.load(sys.stdin)['permissions'].get('directories', 700))")
    local file_permissions=$(echo "$config" | python3 -c "import json, sys; print(json.load(sys.stdin)['permissions'].get('active_logs', 600))")
    
    if [ ! -d "$log_dir" ]; then
        log_warning "Directory not found: $log_dir"
        # Create directory if it doesn't exist
        if mkdir -p "$log_dir" 2>/dev/null; then
            log_info "Created directory: $log_dir"
            # Set secure permissions
            if [ "$(get_platform)" != "windows" ]; then
                chmod "$dir_permissions" "$log_dir" 2>/dev/null || true
            fi
        else
            log_error "Cannot create directory: $log_dir"
            return 1
        fi
    fi
    
    log_info "Rotating: $log_dir (keep ${active_days}d active, ${compressed_days}d compressed)"
    
    # Ensure directory permissions are secure
    if [ "$(get_platform)" != "windows" ]; then
        chmod "$dir_permissions" "$log_dir" 2>/dev/null || log_warning "Could not set permissions on $log_dir"
    fi
    
    local active_count=0
    local compressed_count=0
    local rotated_count=0
    
    # Process .log files for rotation
    while IFS= read -r -d '' log_file; do
        if [ -z "$log_file" ]; then continue; fi
        
        local filename=$(basename "$log_file")
        local file_age_days=$(( ( $(date +%s) - $(date -r "$log_file" +%s) ) / 86400 ))
        
        # Skip current day's log file
        if [[ "$filename" == "$(date +%Y%m%d).log" ]]; then
            ((active_count++))
            continue
        fi
        
        if [ "$file_age_days" -gt "$active_days" ]; then
            # Compress old log files
            if secure_compress "$log_file" "$compression_enabled"; then
                ((rotated_count++))
            fi
        else
            ((active_count++))
        fi
        
        # Set secure permissions on active log files
        if [ "$(get_platform)" != "windows" ]; then
            chmod "$file_permissions" "$log_file" 2>/dev/null || true
        fi
        
    done < <(safe_find "$log_dir" "*.log" -print0 2>/dev/null)
    
    # Remove very old compressed logs
    while IFS= read -r -d '' compressed_file; do
        if [ -z "$compressed_file" ]; then continue; fi
        
        local file_age_days=$(( ( $(date +%s) - $(date -r "$compressed_file" +%s) ) / 86400 ))
        
        if [ "$file_age_days" -gt "$compressed_days" ]; then
            secure_delete "$compressed_file" "older than ${compressed_days} days"
        else
            ((compressed_count++))
            
            # Set secure permissions on compressed files
            if [ "$(get_platform)" != "windows" ]; then
                chmod 600 "$compressed_file" 2>/dev/null || true
            fi
        fi
    done < <(safe_find "$log_dir" "*.log.gz" -print0 2>/dev/null)
    
    # Create new log file for today if it doesn't exist
    local today_log="$log_dir/$(date +%Y%m%d).log"
    if [ ! -f "$today_log" ]; then
        if touch "$today_log" 2>/dev/null; then
            log_info "Created: $(basename "$today_log")"
            # Set secure permissions
            if [ "$(get_platform)" != "windows" ]; then
                chmod "$file_permissions" "$today_log" 2>/dev/null || true
            fi
        else
            log_warning "Failed to create: $today_log"
        fi
    fi
    
    echo "   Active: $active_count logs, Compressed: $compressed_count, Rotated: $rotated_count"
    return 0
}

# Disk space monitoring and emergency cleanup
check_disk_space() {
    local log_root="$BLUX_ROOT/logs"
    local threshold_gb=${1:-1}  # Default 1GB threshold
    
    if [ ! -d "$log_root" ]; then
        return 0
    fi
    
    local platform=$(get_platform)
    local available_space=0
    
    case "$platform" in
        windows)
            available_space=$(df --output=avail "$log_root" | tail -1 | awk '{print $1/1024/1024}')
            ;;
        *)
            available_space=$(df --output=avail "$log_root" 2>/dev/null | tail -1 | awk '{print $1/1024/1024}' || \
                            df -m "$log_root" 2>/dev/null | tail -1 | awk '{print $4/1024}')
            ;;
    esac
    
    if (( $(echo "$available_space < $threshold_gb" | bc -l 2>/dev/null || echo "0") )); then
        log_warning "Low disk space: ${available_space}GB available"
        
        # Emergency cleanup - remove oldest compressed logs
        local emergency_cleaned=0
        while IFS= read -r -d '' old_file; do
            if [ $emergency_cleaned -ge 10 ]; then break; fi  # Clean max 10 files
            secure_delete "$old_file" "emergency disk space cleanup"
            ((emergency_cleaned++))
        done < <(safe_find "$log_root" "*.log.gz" -print0 2>/dev/null | xargs -0 ls -rt 2>/dev/null)
        
        if [ $emergency_cleaned -gt 0 ]; then
            log_info "Emergency cleanup removed $emergency_cleaned old log files"
        fi
    fi
}

# Rotation lock to prevent concurrent executions
acquire_rotation_lock() {
    local lock_timeout=300  # 5 minutes
    
    if [ -f "$ROTATION_LOCK" ]; then
        local lock_age=$(( $(date +%s) - $(date -r "$ROTATION_LOCK" +%s) ))
        if [ "$lock_age" -lt "$lock_timeout" ]; then
            log_error "Log rotation already in progress (lock file exists)"
            log_info "If this is an error, remove: $ROTATION_LOCK"
            return 1
        else
            log_warning "Removing stale lock file"
            rm -f "$ROTATION_LOCK"
        fi
    fi
    
    echo "$$ $(date)" > "$ROTATION_LOCK"
    chmod 600 "$ROTATION_LOCK" 2>/dev/null || true
    return 0
}

release_rotation_lock() {
    rm -f "$ROTATION_LOCK" 2>/dev/null || true
}

# Main rotation function
perform_rotation() {
    local config=$(load_config)
    
    echo -e "${BLUE}"
    echo "📁 BLUX Guard Log Rotation v2.0.0"
    echo "════════════════════════════════"
    echo -e "${NC}"
    
    # Acquire lock to prevent concurrent rotations
    if ! acquire_rotation_lock; then
        exit 1
    fi
    
    # Ensure lock is released on exit
    trap release_rotation_lock EXIT
    
    # Validate dependencies
    if ! validate_dependencies; then
        log_warning "Continuing with limited functionality"
    fi
    
    # Create default config if missing
    create_default_config
    
    # Check disk space before starting
    check_disk_space 1
    
    # Get log directories from config
    local log_dirs=$(echo "$config" | python3 -c "
import json, sys
try:
    config = json.load(sys.stdin)
    directories = config.get('log_directories', [])
    print(' '.join(directories))
except:
    print('logs/anti_tamper logs/sensors logs/decisions')
")
    
    log_info "Starting log rotation process..."
    local total_dirs=0
    local successful_dirs=0
    
    # Rotate each log directory
    for log_dir in $log_dirs; do
        ((total_dirs++))
        if rotate_logs "$log_dir" "$config"; then
            ((successful_dirs++))
        else
            log_error "Failed to rotate: $log_dir"
        fi
    done
    
    # Final disk space check
    check_disk_space 1
    
    # Summary
    echo
    if [ "$successful_dirs" -eq "$total_dirs" ]; then
        log_success "Log rotation completed successfully"
        log_info "Rotated $successful_dirs of $total_dirs directories"
    else
        log_warning "Log rotation completed with errors"
        log_info "Successfully rotated $successful_dirs of $total_dirs directories"
    fi
    
    # Security considerations
    if is_root; then
        log_info "Running as root - all log files secured with restrictive permissions"
    else
        log_info "Running as user - log permissions set for user access only"
    fi
}

# Handle command line arguments
case "${1:-}" in
    "--config")
        create_default_config
        log_success "Configuration file: $LOG_CONFIG"
        ;;
    "--cleanup")
        log_info "Performing emergency disk cleanup..."
        check_disk_space 0.5  # More aggressive cleanup
        ;;
    "--verify")
        log_info "Verifying log directories and permissions..."
        config=$(load_config)
        log_dirs=$(echo "$config" | python3 -c "import json, sys; print(' '.join(json.load(sys.stdin).get('log_directories', [])))")
        for dir in $log_dirs; do
            if [ -d "$dir" ]; then
                local file_count=$(safe_find "$dir" "*.log" | wc -l)
                local compressed_count=$(safe_find "$dir" "*.log.gz" | wc -l)
                echo "✅ $dir: $file_count active, $compressed_count compressed"
            else
                echo "❌ $dir: Missing"
            fi
        done
        ;;
    "--help" | "-h")
        echo "BLUX Guard Log Rotation"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --config      Create/display configuration file"
        echo "  --cleanup     Emergency disk space cleanup"
        echo "  --verify      Verify log directories and files"
        echo "  --help, -h    Show this help message"
        echo
        echo "Features:"
        echo "  • Cross-platform compatibility (Linux, macOS, Windows, Termux)"
        echo "  • Configurable retention policies"
        echo "  • Secure file permissions"
        echo "  • Disk space monitoring"
        echo "  • Concurrent execution protection"
        echo "  • Emergency cleanup procedures"
        echo
        echo "Configuration: $LOG_CONFIG"
        ;;
    *)
        perform_rotation "$@"
        ;;
esac
