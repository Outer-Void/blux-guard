#!/usr/bin/env bash

# ===============================================
# setup_env.sh - Environment setup for BLUX Guard
# Cross-platform compatibility with security enhancements
# Version: 1.0.0
# Author: Outer Void Team
# ===============================================

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || {
    log_error "Cannot change to project root: $PROJECT_ROOT"
    exit 1
}

log_info "BLUX Guard Environment Setup v1.0.0"
log_info "Project root: $PROJECT_ROOT"

# Enhanced environment detection
detect_environment() {
    local env_type="unknown"
    
    # Android detection
    if [[ "$OSTYPE" == "linux-android"* ]] || [[ -d "/system/app" ]] || [[ -d "/system/priv-app" ]]; then
        env_type="android"
    # Termux detection
    elif [[ -d "/data/data/com.termux/files/usr" ]] || [[ -n "$TERMUX_VERSION" ]]; then
        env_type="termux"
    # WSL2 detection
    elif grep -q Microsoft /proc/version 2>/dev/null || [[ -d "/mnt/c/Windows" ]]; then
        env_type="wsl2"
    # macOS detection
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        env_type="macos"
    # Linux detection
    elif [[ "$OSTYPE" == "linux"* ]]; then
        env_type="linux"
    # Windows detection (Git Bash, Cygwin)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        env_type="windows"
    fi
    
    echo "$env_type"
}

ENVIRONMENT=$(detect_environment)
log_info "Detected environment: $ENVIRONMENT"

# Python detection and setup
setup_python() {
    local python_cmd=""
    local pip_cmd=""
    
    case "$ENVIRONMENT" in
        "termux"|"android")
            python_cmd="python"
            pip_cmd="pip"
            ;;
        "windows")
            # Windows environments
            if command -v python3 >/dev/null 2>&1; then
                python_cmd="python3"
                pip_cmd="pip3"
            elif command -v python >/dev/null 2>&1; then
                python_cmd="python"
                pip_cmd="pip"
            else
                log_error "Python not found on Windows. Please install Python 3.7+"
                exit 1
            fi
            ;;
        *)
            # Unix-like environments
            if command -v python3 >/dev/null 2>&1; then
                python_cmd="python3"
                pip_cmd="pip3"
            elif command -v python >/dev/null 2>&1; then
                python_cmd="python"
                pip_cmd="pip"
            else
                log_error "Python not found. Please install Python 3.7+"
                exit 1
            fi
            ;;
    esac
    
    # Verify Python version
    local version
    version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
    
    if [[ "$version" < "3.7" ]]; then
        log_error "Python 3.7+ required. Found: $version"
        exit 1
    fi
    
    log_success "Using Python: $($python_cmd --version) at $(command -v $python_cmd)"
    echo "$python_cmd" "$pip_cmd"
}

# Platform-specific environment setup
setup_environment() {
    log_info "Setting up $ENVIRONMENT environment..."
    
    case "$ENVIRONMENT" in
        "termux"|"android")
            setup_termux
            ;;
        "wsl2")
            setup_wsl2
            ;;
        "macos")
            setup_macos
            ;;
        "linux")
            setup_linux
            ;;
        "windows")
            setup_windows
            ;;
        *)
            log_error "Unsupported environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

setup_termux() {
    log_info "Setting up Termux environment..."
    
    # Update package lists
    if command -v pkg; then
      if ! pkg update -y; then
          log_warning "Failed to update Termux packages, continuing anyway..."
      fi
      
      # Install essential packages
      local packages=(python rust binutils libjpeg-turbo python-numpy libxml2 libxslt)
      for pkg in "${packages[@]}"; do
          if ! pkg list-installed | grep -q "$pkg"; then
              log_info "Installing $pkg..."
              pkg install "$pkg" -y || log_warning "Failed to install $pkg"
          fi
      done
    fi
    
    # Upgrade pip
    if command -v pip; then
      if pip install --upgrade pip; then
          log_success "pip upgraded successfully"
      else
          log_warning "Failed to upgrade pip, continuing anyway..."
      fi
    fi
}

setup_wsl2() {
    log_info "Setting up WSL2 environment..."
    
    # Detect distribution
    if command -v apt-get; then
        # Ubuntu/Debian
        sudo apt update || log_warning "Failed to update package lists"
        sudo apt install -y python3 python3-pip python3-venv build-essential \
                          python3-dev libjpeg-dev zlib1g-dev || log_warning "Some packages failed to install"
    elif command -v dnf; then
        # Fedora
        sudo dnf install -y python3 python3-pip python3-virtualenv @development-tools \
                          python3-devel libjpeg-turbo-devel zlib-devel || log_warning "Some packages failed to install"
    else
        log_warning "Unsupported WSL2 distribution, attempting to continue..."
    fi
}

setup_macos() {
    log_info "Setting up macOS environment..."
    
    # Check for Homebrew
    if command -v brew; then
      log_info "Installing Homebrew..."
        if ! command -v curl; then
          log_error "cURL not found. Homebrew installation requires curl."
        exit 1
        fi

      if [[ ! -d "/opt/homebrew/bin" && ! -d "/usr/local/bin" ]]; then
          log_warning "No brew binary directory detected."
          exit 1
      fi

      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
          log_error "Homebrew installation failed"
          exit 1
      }
        
      # Add Homebrew to PATH for current session
      if [[ -x /opt/homebrew/bin/brew ]]; then
          eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [[ -x /usr/local/bin/brew ]]; then
          eval "$(/usr/local/bin/brew shellenv)"
      fi
      
      # Install Python and dependencies
      brew install python3 || log_warning "Python installation may have issues"
      
      # Install system dependencies
      brew install libjpeg zlib || log_warning "Some dependencies failed to install"
    fi
}

setup_linux() {
    log_info "Setting up Linux environment..."
    
    if command -v apt-get; then
        # Debian/Ubuntu
        sudo apt update || log_warning "Failed to update package lists"
        sudo apt install -y python3 python3-pip python3-venv build-essential \
                          python3-dev libjpeg-dev zlib1g-dev || log_warning "Some packages failed to install"
                          
    elif command -v dnf; then
        # Fedora/RHEL 8+
        sudo dnf install -y python3 python3-pip python3-virtualenv @development-tools \
                          python3-devel libjpeg-turbo-devel zlib-devel || log_warning "Some packages failed to install"
                          
    elif command -v yum; then
        # RHEL/CentOS 7
        sudo yum groupinstall -y "Development Tools" || log_warning "Development tools installation failed"
        sudo yum install -y python3 python3-pip python3-devel libjpeg-turbo-devel zlib-devel || log_warning "Some packages failed to install"
        
    elif command -v pacman; then
        # Arch Linux
        sudo pacman -Syu --noconfirm || log_warning "System update failed"
        sudo pacman -S --noconfirm python python-pip base-devel \
                   python-virtualenv jpegoptim zlib || log_warning "Some packages failed to install"
                   
    elif command -v zypper; then
        # openSUSE
        sudo zypper refresh || log_warning "Package refresh failed"
        sudo zypper install -y python3 python3-pip python3-virtualenv \
                             patterns-devel-base-devel_basis python3-devel \
                             libjpeg8-devel zlib-devel || log_warning "Some packages failed to install"
    else
        log_warning "Unsupported Linux distribution. Attempting to continue with basic setup..."
    fi
}

setup_windows() {
    log_info "Setting up Windows environment..."
    
    # Check if we're in Git Bash, Cygwin, or similar
    if [[ "$OSTYPE" == "msys" ]]; then
        log_info "Detected Git Bash/MINGW environment"
        # Git Bash specific setup
        if ! command -v python3 && ! command -v python; then
            log_error "Python not found. Please install Python 3.7+ from https://python.org"
            log_info "Make sure to check 'Add Python to PATH' during installation"
            exit 1
        fi
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        log_info "Detected Cygwin environment"
        # Cygwin setup would go here
    fi
    
    log_warning "Windows support is experimental. Some features may be limited."
}

# Dependency installation
install_deps() {
    local pip_cmd=$1
    local requirements_file="$PROJECT_ROOT/requirements.txt"
    local file_exists=1

    if [[ ! -f "$requirements_file" ]]; then
        local file_exists=0
        log_error "requirements.txt not found at $requirements_file"
        log_info "Creating basic requirements file..."
    fi
    
    if [[ $file_exists == 0 ]]; then
        cat > "$requirements_file" << 'EOF'
# BLUX Guard Core Dependencies
psutil>=5.8.0
rich>=10.0.0
textual>=0.1.18
cryptography>=3.4.0
argon2-cffi>=21.1.0

# Optional Dependencies (comment out if not needed)
# watchdog>=2.1.0
# requests>=2.25.0
EOF
        log_success "Created basic requirements.txt"
    fi
    
    log_info "Installing Python dependencies..."
    
    # Install requirements
    if "$pip_cmd" install -r "$requirements_file"; then
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install some dependencies"
        log_info "Attempting to install core dependencies individually..."
        
        # Try installing core deps individually
        local core_deps=("psutil>=5.8.0" "rich>=10.0.0" "textual>=0.1.18" "cryptography>=3.4.0" "argon2-cffi>=21.1.0")
        for dep in "${core_deps[@]}"; do
            log_info "Installing $dep..."
            if "$pip_cmd" install "$dep"; then
                log_success "Installed $dep"
            else
                log_error "Failed to install $dep"
            fi
        done
    fi
}

# Post-installation setup
post_install_setup() {
    log_info "Running post-installation setup..."
    
    # Create necessary directories
    local dirs=("logs/anti_tamper" "logs/sensors" "logs/decisions" "scripts" "docs/assets")
    for dir in "${dirs[@]}"; do
        if mkdir -p "$PROJECT_ROOT/$dir"; then
            log_success "Created directory: $dir"
        else
            log_warning "Failed to create directory: $dir"
        fi
    done
    
    # Create default config if missing
    local config_dir="$PROJECT_ROOT/.config/blux_guard"
    if [[ ! -d "$config_dir" ]]; then
        if mkdir -p "$config_dir"; then
            log_success "Created config directory: $config_dir"
            # Create basic motd file
            if [[ ! -f "$config_dir/motd_header.txt" ]]; then
                cat > "$config_dir/motd_header.txt" << 'EOF'
BLUX Guard Security System
Version 1.0.0 - Outer Void Team
EOF
            fi
        fi
    fi
    
    # Verify basic functionality
    log_info "Verifying installation..."
    if python -c "import psutil, rich, cryptography" 2>/dev/null; then
        log_success "Core dependencies verified"
    else
        log_warning "Some core dependencies may not be properly installed"
    fi
}

# Security checks
run_security_checks() {
    log_info "Running security checks..."
    
    # Check for world-writable directories
    local sensitive_dirs=("$PROJECT_ROOT/blux_modules" "$PROJECT_ROOT/.config")
    for dir in "${sensitive_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            local perms
            perms=$(stat -c "%a" "$dir" 2>/dev/null || stat -f "%A" "$dir" 2>/dev/null || echo "unknown")
            if [[ "$perms" == "777" || "$perms" == "775" ]]; then
                log_warning "Insecure permissions on $dir: $perms"
            fi
        fi
    done
    
    # Check for requirements file integrity
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        if grep -q "http://" "$PROJECT_ROOT/requirements.txt"; then
            log_warning "requirements.txt contains insecure HTTP URLs"
        fi
    fi
}

main() {
    log_info "Starting BLUX Guard environment setup..."
    
    # Get Python commands
    local python_commands
    python_commands=$(setup_python)
    local python_cmd pip_cmd
    python_cmd=$(echo "$python_commands" | cut -d' ' -f1)
    pip_cmd=$(echo "$python_commands" | cut -d' ' -f2)
    
    # Run setup
    setup_environment
    install_deps "$pip_cmd"
    post_install_setup
    run_security_checks
    
    log_success "Environment setup completed successfully!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Run the application: ./scripts/run_guard.sh"
    log_info "2. On first run, you'll be prompted to set up a security password"
    log_info "3. Review the logs in: $PROJECT_ROOT/logs/"
    
    log_info ""
    log_info "To create or activate a virtual environment, see ./create_venv.sh"
    
    # Display environment summary
    log_info ""
    log_info "Environment Summary:"
    log_info "  - Platform: $ENVIRONMENT"
    log_info "  - Python: $($python_cmd --version 2>&1)"
    log_info "  - Project: $PROJECT_ROOT"
}

# Handle script interrupts
trap 'log_error "Setup interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
