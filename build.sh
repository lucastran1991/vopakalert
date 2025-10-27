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
    pip3 install --break-system-packages pyinstaller 2>/dev/null || pip install pyinstaller
else
    print_success "PyInstaller is installed"
    echo "   Version: $(pyinstaller --version)"
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist *.spec.bak 2>/dev/null || true
echo "   Cleaned build/ and dist/ directories"

# Generate timestamp for build name
EPOCH=$(date +%s)
BUILD_NAME="main_${EPOCH}"

print_status "Building exe file with name: $BUILD_NAME..."

# Build with custom name
if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # macOS/Linux - no .exe extension
    pyinstaller --name "$BUILD_NAME" --windowed --onefile main.py
else
    # Windows
    pyinstaller --name "$BUILD_NAME" --windowed --onefile --console=False main.py
fi

# Check if build succeeded (cross-platform: .exe for Windows, no extension for Unix)
if [ -f "dist/${BUILD_NAME}.exe" ]; then
    EXE_NAME="${BUILD_NAME}.exe"
elif [ -f "dist/${BUILD_NAME}" ]; then
    EXE_NAME="${BUILD_NAME}"
else
    print_error "Build failed! Executable not found."
    print_error "Looking for: dist/$BUILD_NAME or dist/${BUILD_NAME}.exe"
    if [ -d "dist" ]; then
        print_error "Files in dist/:"
        ls -lh dist/ || true
    fi
    exit 1
fi

FILE_SIZE=$(du -h "dist/$EXE_NAME" | cut -f1)
print_success "Build successful!"
echo "   Output: dist/$EXE_NAME"
echo "   Size: $FILE_SIZE"

# Optional: Show file info
if command -v file &> /dev/null; then
    echo "   Type: $(file dist/$EXE_NAME)"
fi

echo ""
print_success "Build process completed!"
