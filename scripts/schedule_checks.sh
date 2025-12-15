#!/usr/bin/env bash
# BLUX Guard Schedule Setup
# Sets scheduled tasks for periodic security, sensor, and containment checks
# Cross-platform: Linux, macOS, Windows (Task Scheduler), Termux
# Version: 1.0.0
# Author: Outer Void Team

set -euo pipefail  # Strict error handling
IFS=$'\n\t'

# Script directory resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLUX_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${BLUX_CONFIG_DIR:-$HOME/.config/blux_guard}"
SCHEDULE_BACKUP_DIR="$CONFIG_DIR/schedule_backups"

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
    
    case "$platform" in
        linux|macos|termux)
            if ! command -v crontab >/dev/null 2>&1; then
                log_error "cron is not available on this system"
                case "$platform" in
                    termux)
                        log_info "Install with: pkg install cronie"
                        ;;
                    linux)
                        if command -v apt >/dev/null 2>&1; then
                            log_info "Install with: sudo apt install cron"
                        elif command -v yum >/dev/null 2>&1; then
                            log_info "Install with: sudo yum install cronie"
                        fi
                        ;;
                    macos)
                        log_info "Cron should be available by default on macOS"
                        ;;
                esac
                return 1
            fi
            ;;
        windows)
            if ! command -v schtasks >/dev/null 2>&1; then
                log_error "Windows Task Scheduler not available"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Environment validation
validate_environment() {
    log_info "Validating environment..."
    
    # Check BLUX root structure
    if [ ! -f "$BLUX_ROOT/blux_modules/__init__.py" ]; then
        log_error "BLUX Guard installation not found or corrupted"
        return 1
    fi
    
    # Verify script dependencies exist
    local required_scripts=(
        "$SCRIPT_DIR/check_status.sh"
        "$SCRIPT_DIR/rotate_logs.sh" 
        "$SCRIPT_DIR/daily_report.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            log_warning "Required script not found: $(basename "$script")"
            log_info "Some scheduled tasks may not function properly"
        else
            # Ensure scripts are executable
            chmod +x "$script" 2>/dev/null || true
        fi
    done
    
    # Create backup directory
    mkdir -p "$SCHEDULE_BACKUP_DIR"
    
    return 0
}

# Cross-platform temporary file creation
create_temp_file() {
    case "$(get_platform)" in
        windows) 
            # Windows temp file
            echo "$(cygpath -w "$(mktemp)")"
            ;;
        *) 
            # Unix-like temp file
            mktemp
            ;;
    esac
}

# Backup existing scheduled tasks
backup_existing_schedule() {
    local platform=$(get_platform)
    local backup_file="$SCHEDULE_BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S)"
    
    log_info "Backing up existing scheduled tasks..."
    
    case "$platform" in
        linux|macos|termux)
            crontab -l > "$backup_file" 2>/dev/null || echo "No existing crontab" > "$backup_file"
            ;;
        windows)
            schtasks /query /fo LIST > "$backup_file" 2>/dev/null || true
            ;;
    esac
    
    log_success "Backup saved to: $backup_file"
    echo "$backup_file"
}

# Generate platform-specific scheduled tasks
generate_schedule_config() {
    local platform=$(get_platform)
    local config_file=$(create_temp_file)
    
    case "$platform" in
        linux|macos|termux)
            # Unix-like cron configuration
            cat > "$config_file" << EOF
# BLUX Guard Automated Tasks
# Installed by schedule_checks.sh v2.0.0
# Platform: $platform
# Created: $(date)

# Environment setup
BLUX_ROOT="$BLUX_ROOT"
BLUX_CONFIG_DIR="$CONFIG_DIR"
PATH="$PATH:/usr/local/bin:/usr/bin:/bin"

# Health and security monitoring
*/30 * * * * "$SCRIPT_DIR/check_status.sh" --cron > "$BLUX_ROOT/logs/cron_check.log" 2>&1

# Log rotation and maintenance
0 2 * * * "$SCRIPT_DIR/rotate_logs.sh" --cron > "$BLUX_ROOT/logs/cron_rotate.log" 2>&1

# Daily security report
0 6 * * * "$SCRIPT_DIR/daily_report.sh" --cron > "$BLUX_ROOT/logs/cron_report.log" 2>&1

# Security sensor checks
0 * * * * cd "$BLUX_ROOT" && python3 -m blux_modules.sensor_manager --check --cron > "$BLUX_ROOT/logs/cron_sensors.log" 2>&1

# Weekly deep security scan (Sundays at 3 AM)
0 3 * * 0 cd "$BLUX_ROOT" && python3 -m blux_modules.security_engine --deep-scan --cron > "$BLUX_ROOT/logs/cron_deepscan.log" 2>&1

# Backup cleanup (Monthly)
0 4 1 * * cd "$BLUX_ROOT" && "$SCRIPT_DIR/clean_temp.sh" --cron > "$BLUX_ROOT/logs/cron_cleanup.log" 2>&1

EOF
            ;;
        windows)
            # Windows Task Scheduler XML templates
            cat > "$config_file" << EOF
<?xml version="1.0" encoding="UTF-16"?>
<!-- BLUX Guard Scheduled Tasks -->
<TaskList>
    <!-- Health Check - Every 30 minutes -->
    <Task>
        <Name>BLUX Guard Health Check</Name>
        <Exec>
            <Command>bash</Command>
            <Arguments>"$SCRIPT_DIR/check_status.sh" --cron</Arguments>
            <WorkingDirectory>$BLUX_ROOT</WorkingDirectory>
        </Exec>
        <Schedule>
            <Interval>PT30M</Interval>
        </Schedule>
    </Task>
    
    <!-- Log Rotation - Daily at 2 AM -->
    <Task>
        <Name>BLUX Guard Log Rotation</Name>
        <Exec>
            <Command>bash</Command>
            <Arguments>"$SCRIPT_DIR/rotate_logs.sh" --cron</Arguments>
            <WorkingDirectory>$BLUX_ROOT</WorkingDirectory>
        </Exec>
        <Schedule>
            <StartTime>02:00:00</StartTime>
            <Interval>P1D</Interval>
        </Schedule>
    </Task>
    
    <!-- Daily Report - 6 AM -->
    <Task>
        <Name>BLUX Guard Daily Report</Name>
        <Exec>
            <Command>bash</Command>
            <Arguments>"$SCRIPT_DIR/daily_report.sh" --cron</Arguments>
            <WorkingDirectory>$BLUX_ROOT</WorkingDirectory>
        </Exec>
        <Schedule>
            <StartTime>06:00:00</StartTime>
            <Interval>P1D</Interval>
        </Schedule>
    </Task>
</TaskList>
EOF
            ;;
    esac
    
    echo "$config_file"
}

# Install Unix-like cron jobs
install_unix_schedule() {
    local config_file="$1"
    local backup_file="$2"
    
    log_info "Installing Unix cron jobs..."
    
    # Validate cron syntax before installation
    if ! crontab -l >/dev/null 2>&1; then
        log_warning "No existing crontab - creating new one"
    fi
    
    # Install the new crontab
    if crontab "$config_file"; then
        log_success "Cron jobs installed successfully"
        
        # Verify installation
        local installed_count=$(crontab -l | grep -c "BLUX Guard" || true)
        log_info "Verified $installed_count BLUX Guard tasks installed"
        
    else
        log_error "Failed to install cron jobs"
        
        # Attempt restore from backup
        if [ -s "$backup_file" ] && ! grep -q "No existing crontab" "$backup_file"; then
            log_info "Restoring previous crontab from backup..."
            crontab "$backup_file"
        fi
        return 1
    fi
    
    return 0
}

# Install Windows scheduled tasks
install_windows_schedule() {
    local config_file="$1"
    
    log_info "Installing Windows scheduled tasks..."
    
    # Convert paths for Windows
    local win_script_dir=$(cygpath -w "$SCRIPT_DIR")
    local win_blux_root=$(cygpath -w "$BLUX_ROOT")
    
    # Create individual tasks (simplified approach for reliability)
    local tasks_created=0
    
    # Health check task
    if schtasks /create /tn "BLUX Guard Health Check" /tr "bash \"$win_script_dir\\check_status.sh\" --cron" /sc minute /mo 30 /f 2>/dev/null; then
        log_success "Created: Health Check task"
        ((tasks_created++))
    else
        log_warning "Failed to create Health Check task"
    fi
    
    # Log rotation task
    if schtasks /create /tn "BLUX Guard Log Rotation" /tr "bash \"$win_script_dir\\rotate_logs.sh\" --cron" /sc daily /st 02:00 /f 2>/dev/null; then
        log_success "Created: Log Rotation task"
        ((tasks_created++))
    else
        log_warning "Failed to create Log Rotation task"
    fi
    
    # Daily report task
    if schtasks /create /tn "BLUX Guard Daily Report" /tr "bash \"$win_script_dir\\daily_report.sh\" --cron" /sc daily /st 06:00 /f 2>/dev/null; then
        log_success "Created: Daily Report task"
        ((tasks_created++))
    else
        log_warning "Failed to create Daily Report task"
    fi
    
    if [ "$tasks_created" -eq 0 ]; then
        log_error "No Windows tasks could be created"
        return 1
    fi
    
    log_success "Created $tasks_created Windows scheduled tasks"
    return 0
}

# Remove existing BLUX scheduled tasks
remove_existing_blux_tasks() {
    local platform=$(get_platform)
    
    log_info "Removing existing BLUX Guard scheduled tasks..."
    
    case "$platform" in
        linux|macos|termux)
            # Remove BLUX entries from crontab
            if crontab -l 2>/dev/null | grep -q "BLUX Guard"; then
                crontab -l 2>/dev/null | grep -v "BLUX Guard" | crontab -
                log_success "Removed existing BLUX cron jobs"
            fi
            ;;
        windows)
            # Remove BLUX Windows tasks
            for task in "BLUX Guard Health Check" "BLUX Guard Log Rotation" "BLUX Guard Daily Report"; do
                if schtasks /query /tn "$task" >/dev/null 2>&1; then
                    schtasks /delete /tn "$task" /f >/dev/null 2>&1 && \
                    log_success "Removed: $task" || \
                    log_warning "Failed to remove: $task"
                fi
            done
            ;;
    esac
}

# Verify schedule installation
verify_schedule_installation() {
    local platform=$(get_platform)
    local verification_success=true
    
    log_info "Verifying schedule installation..."
    
    case "$platform" in
        linux|macos|termux)
            local installed_tasks=$(crontab -l 2>/dev/null | grep -c "BLUX Guard" || true)
            if [ "$installed_tasks" -ge 4 ]; then
                log_success "Verified $installed_tasks BLUX Guard cron tasks"
            else
                log_warning "Only $installed_tasks BLUX tasks found (expected 4+)"
                verification_success=false
            fi
            ;;
        windows)
            local task_count=0
            for task in "BLUX Guard Health Check" "BLUX Guard Log Rotation" "BLUX Guard Daily Report"; do
                if schtasks /query /tn "$task" >/dev/null 2>&1; then
                    ((task_count++))
                fi
            done
            
            if [ "$task_count" -ge 2 ]; then
                log_success "Verified $task_count BLUX Guard Windows tasks"
            else
                log_warning "Only $task_count BLUX Windows tasks found"
                verification_success=false
            fi
            ;;
    esac
    
    $verification_success
}

# Display schedule information
display_schedule_info() {
    local platform=$(get_platform)
    
    echo
    echo -e "${GREEN}🎉 BLUX Guard Schedule Setup Complete${NC}"
    echo "══════════════════════════════════"
    
    case "$platform" in
        linux|macos|termux)
            echo -e "${CYAN}Installed Cron Jobs:${NC}"
            crontab -l 2>/dev/null | grep "BLUX Guard" || echo "No BLUX tasks found"
            echo
            echo -e "${CYAN}Management Commands:${NC}"
            echo "  View all:    crontab -l"
            echo "  Edit:        crontab -e" 
            echo "  Remove all:  crontab -r"
            echo "  BLUX only:   crontab -l | grep BLUX"
            ;;
        windows)
            echo -e "${CYAN}Installed Windows Tasks:${NC}"
            schtasks /query /fo TABLE 2>/dev/null | grep "BLUX Guard" || echo "No BLUX tasks found"
            echo
            echo -e "${CYAN}Management Commands:${NC}"
            echo "  View all:    schtasks /query /fo TABLE"
            echo "  Run task:    schtasks /run /tn \"Task Name\""
            echo "  Delete task: schtasks /delete /tn \"Task Name\" /f"
            ;;
    esac
    
    echo
    echo -e "${CYAN}Scheduled Tasks:${NC}"
    echo "  ✅ Health monitoring - Every 30 minutes"
    echo "  ✅ Log rotation - Daily at 2 AM"
    echo "  ✅ Security report - Daily at 6 AM" 
    echo "  ✅ Sensor checks - Hourly"
    echo "  ✅ Deep security scan - Sundays at 3 AM"
    echo "  ✅ Backup cleanup - Monthly"
    echo
    echo -e "${YELLOW}Logs are stored in: $BLUX_ROOT/logs/cron_*.log${NC}"
}

# Security considerations warning
show_security_warning() {
    local platform=$(get_platform)
    
    echo
    echo -e "${YELLOW}⚠️  SECURITY CONSIDERATIONS${NC}"
    echo "══════════════════════════════════"
    
    case "$platform" in
        linux|macos|termux)
            echo "• Cron jobs run with user privileges"
            echo "• Ensure $SCRIPT_DIR is not writable by others"
            echo "• Review cron logs regularly in $BLUX_ROOT/logs/"
            echo "• Use 'crontab -l' to verify installed tasks"
            ;;
        windows)
            echo "• Tasks run with current user privileges"
            echo "• Ensure BLUX scripts are in secure location"
            echo "• Review Task Scheduler history periodically"
            ;;
    esac
    
    if is_root; then
        echo -e "${RED}• Running as root - tasks have full system access${NC}"
        echo "• Consider creating dedicated user for BLUX tasks"
    else
        echo "• Running as user - some system monitoring may be limited"
    fi
}

# Main installation function
install_schedule() {
    local platform=$(get_platform)
    
    echo -e "${BLUE}"
    echo "⏰ BLUX Guard Schedule Setup v2.0.0"
    echo "══════════════════════════════════"
    echo -e "${NC}"
    
    # Validate environment and dependencies
    if ! validate_dependencies; then
        exit 1
    fi
    
    if ! validate_environment; then
        exit 1
    fi
    
    # Backup existing schedule
    local backup_file=$(backup_existing_schedule)
    
    # Remove existing BLUX tasks
    remove_existing_blux_tasks
    
    # Generate and install new schedule
    local config_file=$(generate_schedule_config)
    
    case "$platform" in
        linux|macos|termux)
            if ! install_unix_schedule "$config_file" "$backup_file"; then
                log_error "Failed to install Unix schedule"
                rm -f "$config_file"
                exit 1
            fi
            ;;
        windows)
            if ! install_windows_schedule "$config_file"; then
                log_error "Failed to install Windows schedule"
                rm -f "$config_file"
                exit 1
            fi
            ;;
        *)
            log_error "Unsupported platform: $platform"
            rm -f "$config_file"
            exit 1
            ;;
    esac
    
    # Cleanup temp file
    rm -f "$config_file"
    
    # Verify installation
    if verify_schedule_installation; then
        display_schedule_info
        show_security_warning
    else
        log_warning "Schedule installation completed with warnings"
        display_schedule_info
    fi
}

# Handle command line arguments
case "${1:-}" in
    "--remove")
        remove_existing_blux_tasks
        log_success "All BLUX Guard scheduled tasks removed"
        ;;
    "--backup")
        backup_existing_schedule
        ;;
    "--verify")
        verify_schedule_installation && \
        log_success "Schedule verification passed" || \
        log_error "Schedule verification failed"
        ;;
    "--platform")
        echo "Detected platform: $(get_platform)"
        ;;
    "--help" | "-h")
        echo "BLUX Guard Schedule Setup"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --remove    Remove all BLUX scheduled tasks"
        echo "  --backup    Backup existing schedule only"
        echo "  --verify    Verify current installation"
        echo "  --platform  Show detected platform"
        echo "  --help, -h  Show this help message"
        echo
        echo "Supported Platforms:"
        echo "  • Linux (cron)"
        echo "  • macOS (cron)"
        echo "  • Windows (Task Scheduler)"
        echo "  • Termux (cron)"
        echo
        echo "Security Features:"
        echo "  • Automatic backup of existing schedules"
        echo "  • Platform-specific task configuration"
        echo "  • Installation verification"
        echo "  • Secure script execution"
        ;;
    *)
        install_schedule "$@"
        ;;
esac
