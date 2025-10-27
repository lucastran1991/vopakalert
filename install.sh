#!/bin/bash

# Vopak Alert - Installation Script
# Installs required Python dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}🔨 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 is not installed!"
        print_error "Please install Python 3.7 or higher"
        print_error ""
        print_error "Install via Homebrew (macOS):"
        print_error "  brew install python3"
        print_error ""
        print_error "Or download from: https://www.python.org/downloads/"
        return 1
    fi
}

# Function to check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        print_success "pip found: $PIP_VERSION"
        return 0
    else
        print_error "pip3 is not installed!"
        print_warning "Attempting to install pip..."
        
        # Try to install pip
        if command -v python3 &> /dev/null; then
            python3 -m ensurepip --upgrade
            if [ $? -eq 0 ]; then
                print_success "pip installed"
                return 0
            fi
        fi
        
        print_error "Could not install pip automatically"
        return 1
    fi
}

# Main installation function
main() {
    echo "=================================================="
    echo "  VOPAK ALERT - DEPENDENCY INSTALLATION"
    echo "=================================================="
    echo ""
    
    # Check Python
    print_status "Checking Python..."
    if ! check_python; then
        exit 1
    fi
    
    # Check pip
    print_status "Checking pip..."
    if ! check_pip; then
        exit 1
    fi
    
    echo ""
    
    # Determine pip command to use
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    # Upgrade pip first
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip --quiet
    print_success "pip upgraded"
    
    echo ""
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        print_error "Please ensure you're in the project directory"
        exit 1
    fi
    
    print_status "Installing dependencies from requirements.txt..."
    echo ""
    
    # Install dependencies
    if [ "$OSTYPE" == "darwin"* ]; then
        # macOS - try multiple methods
        print_warning "Detected macOS - trying different installation methods..."
        
        if $PIP_CMD install --user -r requirements.txt 2>/dev/null; then
            print_success "Installed with --user flag"
        elif $PIP_CMD install --break-system-packages -r requirements.txt 2>/dev/null; then
            print_success "Installed with --break-system-packages"
        else
            # Regular installation
            print_status "Trying standard installation..."
            $PIP_CMD install -r requirements.txt
        fi
    else
        # Regular installation for Linux/Windows
        $PIP_CMD install -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "All dependencies installed successfully!"
        echo ""
        
        # Verify installation
        print_status "Verifying installed packages..."
        echo ""
        
        $PIP_CMD list | grep -E "(requests|schedule)" || print_warning "Could not verify packages"
        
        echo ""
        print_success "Installation complete!"
        echo ""
        print_status "You can now run the application:"
        echo "  python3 main.py"
        echo ""
    else
        print_error "Installation failed!"
        exit 1
    fi
}

# Handle different platforms
detect_platform() {
    if [ "$OSTYPE" == "darwin"* ]; then
        print_status "Platform: macOS"
        
        # Check for Homebrew Python
        if [ -n "$(brew --prefix 2>/dev/null)" ]; then
            if [ -f "$(brew --prefix)/opt/python@3.13/bin/python3" ] || \
               [ -f "$(brew --prefix)/opt/python/bin/python3" ]; then
                print_warning "Using Homebrew Python"
            fi
        fi
    elif [ "$OSTYPE" == "linux-gnu"* ]; then
        print_status "Platform: Linux"
    elif [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ]; then
        print_status "Platform: Windows (Git Bash/Cygwin)"
    else
        print_status "Platform: Unknown"
    fi
}

# Run main function
detect_platform
echo ""
main

