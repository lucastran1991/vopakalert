#!/usr/bin/env python3
"""
Build script for Vopak Alert
Automatically builds exe from main.spec
"""

import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path

def print_status(msg):
    print(f"🔨 {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def run_command(command):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    success, output = run_command("pyinstaller --version")
    if not success:
        print_status("PyInstaller not found. Installing...")
        # Try installing with different methods
        install_commands = [
            "pip3 install --break-system-packages pyinstaller",
            "pip install --break-system-packages pyinstaller",
            "python3 -m pip install --user pyinstaller",
        ]
        
        for cmd in install_commands:
            success, output = run_command(cmd)
            if success:
                print_success("PyInstaller installed")
                break
        
        if not success:
            print_error("Failed to install PyInstaller")
            print_error("Please install PyInstaller manually:")
            print_error("  pip3 install --break-system-packages pyinstaller")
            print_error("  or use a virtual environment")
            return False
        
        # Verify installation
        success, output = run_command("pyinstaller --version")
        if not success:
            print_error("PyInstaller installed but not accessible")
            return False
    
    print_success(f"PyInstaller version: {output.strip()}")
    return True

def clean_builds():
    """Clean previous builds"""
    print_status("Cleaning previous builds...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

def build_exe():
    """Build exe using spec file"""
    import time
    epoch = int(time.time())
    build_name = f"main_{epoch}"
    
    print_status(f"Building exe file with name: {build_name}...")
    
    # Build with custom name and cross-platform options
    if platform.system() == "Windows":
        cmd = f'pyinstaller --name "{build_name}" --windowed --onefile --console=False main.py'
    else:
        cmd = f'pyinstaller --name "{build_name}" --windowed --onefile main.py'
    
    success, output = run_command(cmd)
    return success, output, build_name

def main():
    print("=" * 50)
    print("VOPAK ALERT BUILD SCRIPT")
    print("=" * 50)
    
    # Check Python version
    print(f"Python: {sys.version}")
    
    # Check PyInstaller
    if not check_pyinstaller():
        sys.exit(1)
    
    # Clean builds
    clean_builds()
    
    # Build exe
    success, output, build_name = build_exe()
    
    if not success:
        print_error("Build failed!")
        print(output)
        sys.exit(1)
    
    # Check result (cross-platform: .exe for Windows, no extension for Unix)
    if platform.system() == "Windows":
        exe_name = f"{build_name}.exe"
    else:
        exe_name = build_name
    
    exe_path = Path(f"dist/{exe_name}")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print_success("Build successful!")
        print(f"   Output: {exe_path}")
        print(f"   Size: {size_mb:.2f} MB")
    else:
        print_error("Build failed! Executable not found.")
        print_error(f"Looking for: {exe_path}")
        # List what's actually in dist/
        if Path("dist").exists():
            print_error("Files in dist/:")
            for f in Path("dist").iterdir():
                print_error(f"  - {f}")
        sys.exit(1)
    
    print("\n✅ Build process completed!")

if __name__ == "__main__":
    main()
