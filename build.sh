#!/bin/bash

# Vopak Alert Build Script (Enhanced Version)
# Build Python app to exe using PyInstaller

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed!"
    exit 1
fi

print_status "Python version: $(python3 --version)"

# Check and install PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    print_warning "PyInstaller not found. Installing..."
    pip install pyinstaller
else
    print_success "PyInstaller is installed"
    echo "   Version: $(pyinstaller --version)"
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist *.spec.bak 2>/dev/null || true
echo "   Cleaned build/ and dist/ directories"

# Build the exe
print_status "Building exe file..."
pyinstaller main.spec

# Check if build succeeded
if [ -f "dist/main.exe" ]; then
    FILE_SIZE=$(du -h dist/main.exe | cut -f1)
    print_success "Build successful!"
    echo "   Output: dist/main.exe"
    echo "   Size: $FILE_SIZE"
    
    # Optional: Show file info
    if command -v file &> /dev/null; then
        echo "   Type: $(file dist/main.exe)"
    fi
else
    print_error "Build failed! Executable not found."
    exit 1
fi

echo ""
print_success "Build process completed!"
