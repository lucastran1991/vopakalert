#!/bin/bash

# Build macOS Application Script for Vopak Alert
# Creates a .app bundle ready for distribution

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}🔨 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is for macOS only!"
    exit 1
fi

print_status "Building macOS Application..."

# Install PyInstaller if needed
if ! command -v pyinstaller &> /dev/null; then
    print_status "Installing PyInstaller..."
    pip3 install --break-system-packages pyinstaller 2>/dev/null || pip install pyinstaller
fi

# Generate app name with timestamp
EPOCH=$(date +%s)
APP_NAME="VopakAlert_${EPOCH}"

print_status "App name: ${APP_NAME}"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist *.spec.bak 2>/dev/null || true

# Build options for macOS
BUILD_OPTIONS=(
    "--windowed"           # No console window
    "--onedir"            # Create app bundle (recommended for macOS)
    "--name=${APP_NAME}"  # App name
    "--clean"             # Clean cache
    "--noconfirm"         # Overwrite without asking
)

# Build the app
print_status "Building .app bundle..."
pyinstaller "${BUILD_OPTIONS[@]}" main.py

# Check if build succeeded
APP_PATH="dist/${APP_NAME}.app"
if [ -d "$APP_PATH" ]; then
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
    print_success "Build successful!"
    echo "   App: $APP_PATH"
    echo "   Size: $APP_SIZE"
    
    # Show app contents
    echo "   Executable: $APP_PATH/Contents/MacOS/$APP_NAME"
    
    # Instructions
    echo ""
    print_success "To run the app:"
    echo "   open \"$APP_PATH\""
    echo ""
    print_success "To test:"
    echo "   \"$APP_PATH/Contents/MacOS/$APP_NAME\""
else
    print_error "Build failed! App bundle not found."
    exit 1
fi

