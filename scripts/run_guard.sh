#!/usr/bin/env bash

# ===============================================
# run_guard.sh — Launch BLUX Guard Cockpit
# Enhanced for multi-environment compatibility
# Version: 1.0.0
# Author: Outer Void Team
# ===============================================

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Detect environment
detect_environment() {
    if [[ "$OSTYPE" == "linux-android"* ]] || [[ -d "/system/app" ]] || [[ -d "/system/priv-app" ]]; then
        echo "android"
    elif [[ -d "/data/data/com.termux/files/usr" ]]; then
        echo "termux"
    elif grep -q Microsoft /proc/version 2>/dev/null || [[ -d "/mnt/c/Windows" ]]; then
        echo "wsl2"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

ENVIRONMENT=$(detect_environment)
echo "BLUX Guard v1.0.0 - Outer Void Team"
echo "Detected environment: $ENVIRONMENT"

# Set project root (robust handling for different invocation methods)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || {
    echo "ERROR: Cannot change to project root: $PROJECT_ROOT"
    exit 1
}

echo "Project root: $PROJECT_ROOT"

# Environment-specific Python configuration
setup_python() {
    case "$ENVIRONMENT" in
        "termux"|"android")
            # Termux/Android specific Python handling
            if command -v pkg >/dev/null 2>&1; then
                echo "Termux environment detected"
                # Ensure required packages are installed
                pkg list-installed | grep -q python || {
                    echo "Installing Python in Termux..."
                    pkg install python -y
                }
            fi
            PYTHON_CMD="python"
            ;;
        "wsl2")
            # WSL2 might have multiple Python installations

            # Check if there's a python executable in the venv first, and use that
            if [[ -d "$PROJECT_ROOT/.venv" ]] && command -v "$PROJECT_ROOT/.venv/bin/python3" >/dev/null 2>&1; then
               PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python3"
            elif command -v python3 >/dev/null 2>&1; then
                PYTHON_CMD="python3"
            elif command -v python >/dev/null 2>&1; then
                PYTHON_CMD="python"
            else
                echo "ERROR: Python not found in WSL2 environment"
                exit 1
            fi

            # Check Python version
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
            if [[ $(printf '%s\n' "$PYTHON_VERSION" "3.7" | sort -Vr | head -n 1) != "3.7" ]]; then
                echo "ERROR: Python version $PYTHON_VERSION is too old. Please install Python 3.7+"
                exit 1
            fi
            ;;
        "macos")
            # macOS typically uses python3
            if command -v python3 >/dev/null 2>&1; then
                PYTHON_CMD="python3"
            else
                echo "ERROR: python3 not found on macOS. Install via Homebrew: brew install python"
                exit 1
            fi
            ;;
        *)
            # Linux and other environments

            # Check if there's a python executable in the venv first, and use that
            if [[ -d "$PROJECT_ROOT/.venv" ]] && command -v "$PROJECT_ROOT/.venv/bin/python3" >/dev/null 2>&1; then
               PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python3"
            elif command -v python3 >/dev/null 2>&1; then
                PYTHON_CMD="python3"
            elif command -v python >/dev/null 2>&1; then
                PYTHON_CMD="python"
            else
                echo "ERROR: Python not found. Please install Python 3.7+"
                exit 1
            fi
            ;;
    esac
    
    echo "Using Python: $(command -v $PYTHON_CMD)"
    $PYTHON_CMD --version || {
        echo "ERROR: Python is not working properly"
        exit 1
    }
}

setup_python

# Virtual environment handling
setup_venv() {
    VENV_DIR="$PROJECT_ROOT/.venv"

    # Check if we should use virtual environment
    if [[ "$ENVIRONMENT" == "termux" || "$ENVIRONMENT" == "android" ]]; then
        echo "Skipping virtual environment on Termux/Android"
        return 0
    fi
    
    if [ -d "$VENV_DIR" ]; then
        echo "Activating virtual environment..."
        # shellcheck source=/dev/null
        source "$VENV_DIR/bin/activate"
    else
        echo "Virtual environment not found at $VENV_DIR"
        echo "Create one with: python3 -m venv .venv"
    fi
}

setup_venv

# Dependency installation
install_dependencies() {
    REQUIREMENTS="$PROJECT_ROOT/requirements.txt"
    
    if [ -f "$REQUIREMENTS" ]; then
        echo "Checking and installing dependencies..."
        
        # Check if we're in a virtual environment or should install globally
        if [[ "$VIRTUAL_ENV" != "" ]] || [[ "$ENVIRONMENT" == "termux" ]] || [[ "$ENVIRONMENT" == "android" ]]; then
            PIP_CMD="pip"
        else
            PIP_CMD="pip3 --user"
        fi
        
        # Upgrade pip first
        $PIP_CMD install --upgrade pip || {
            echo "WARNING: Failed to upgrade pip, continuing anyway..."
        }
        
        # Install requirements
        echo "Installing Python dependencies..."
        $PIP_CMD install -r "$REQUIREMENTS" || {
            echo "ERROR: Failed to install dependencies"
            echo "You may need to install system dependencies first."
            if [[ "$ENVIRONMENT" == "linux" ]]; then
                echo "On Ubuntu/Debian: sudo apt-get install python3-dev python3-venv"
            elif [[ "$ENVIRONMENT" == "macos" ]]; then
                echo "On macOS: xcode-select --install"
            fi
            exit 1
        }
        echo "Dependencies installed successfully"
    else
        echo "WARNING: requirements.txt not found at $REQUIREMENTS"
    fi
}

install_dependencies

# Logs directory setup with proper permissions
setup_logs() {
    LOGS_DIR="$PROJECT_ROOT/logs"
    mkdir -p "$LOGS_DIR" || {
        echo "ERROR: Cannot create logs directory: $LOGS_DIR"
        exit 1
    }
    
    # Create subdirectories
    mkdir -p "$LOGS_DIR/anti_tamper" "$LOGS_DIR/sensors" "$LOGS_DIR/decisions"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="$LOGS_DIR/guard_${TIMESTAMP}.log"
    echo "Log file: $LOG_FILE"
}

setup_logs

# Environment-specific pre-launch checks
pre_launch_checks() {
    case "$ENVIRONMENT" in
        "termux"|"android")
            echo "Running on Termux/Android - some features may be limited"
            # Check for Termux storage permission
            if [[ "$ENVIRONMENT" == "termux" ]] && [ ! -d "/sdcard" ]; then
                echo "NOTE: Termux storage permission might be needed for full functionality"
                echo "Run: termux-setup-storage"
            fi
            ;;
        "wsl2")
            echo "Running on WSL2 - Windows integration features available"
            ;;
        "macos")
            echo "Running on macOS - ensure all required system permissions are granted"
            ;;
    esac
    
    # Check if blux_cli module exists
    if [ ! -f "$PROJECT_ROOT/blux_cli/blux.py" ]; then
        echo "ERROR: blux_cli module not found at $PROJECT_ROOT/blux_cli/blux.py"
        echo "Please ensure you're in the correct directory and the project structure is intact"
        exit 1
    fi
    
    # Check if initiate_cockpit.py exists
    if [ ! -f "$PROJECT_ROOT/initiate_cockpit.py" ]; then
        echo "ERROR: initiate_cockpit.py not found at $PROJECT_ROOT/initiate_cockpit.py"
        exit 1
    fi
}

pre_launch_checks

# Launch BLUX Guard cockpit
echo "Launching BLUX Guard cockpit..."
echo "Environment: $ENVIRONMENT, Python: $PYTHON_CMD"

# Use tee with proper error handling
{
    $PYTHON_CMD initiate_cockpit.py 2>&1
    EXIT_CODE=$?
    echo "BLUX Guard exited with code: $EXIT_CODE"
    exit $EXIT_CODE
} | tee "$LOG_FILE"

# Note: Virtual environment deactivation happens automatically when script exits
echo "BLUX Guard session finished. Log saved to $LOG_FILE"
