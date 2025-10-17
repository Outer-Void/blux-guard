#!/usr/bin/env bash

# ===============================================
# create_venv.sh - Creates a Python virtual environment
# Version: 1.0.0
# Author: Outer Void Team
# ===============================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging functions
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || {
    echo "ERROR: Cannot change to project root: $PROJECT_ROOT"
    exit 1
}

# Check if virtualenv module is installed, otherwise install
if ! python3 -m venv --help &> /dev/null; then
    echo "Installing the 'venv' module..."
    sudo apt update
    sudo apt install python3-venv
    if [[ $? -ne 0 ]]; then
      echo "Error: Could not install the python3-venv package. Exiting script."
      exit 1
    fi
    log_success "Installed 'venv'"
fi

# Define virtual environment directory
VENV_DIR="$PROJECT_ROOT/.venv"

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at: $VENV_DIR"
else
    # Create virtual environment
    echo "Creating virtual environment at: $VENV_DIR"
    python3 -m venv "$VENV_DIR" || {
        echo "ERROR: Failed to create virtual environment"
        exit 1
    }
fi

# Determine activation command based on OS
if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux"* ]]; then
    ACTIVATION_COMMAND="source $VENV_DIR/bin/activate"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    ACTIVATION_COMMAND="source $VENV_DIR/Scripts/activate"
elif [[ "$OSTYPE" == "win32" ]]; then
    ACTIVATION_COMMAND="$VENV_DIR\\Scripts\\activate"
else
    ACTIVATION_COMMAND="source $VENV_DIR/bin/activate" # Default for other UNIX-like systems
fi

# Print instructions for activating the virtual environment
log_success "Virtual environment created successfully!"
echo ""
echo "To activate the virtual environment, run:"
echo "  $ACTIVATION_COMMAND"
echo ""
echo "After activating the virtual environment, run './setup_env.sh' again to continue setup."
echo ""
