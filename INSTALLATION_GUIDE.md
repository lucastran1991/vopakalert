# Installation Guide

## 📦 Dependencies

### External Libraries Required:

- **requests** (>=2.31.0) - For API HTTP calls
- **schedule** (>=1.2.0) - For task scheduling

### Built-in Libraries (No installation needed):

- tkinter - GUI framework
- smtplib - Email sending
- json - JSON parsing
- datetime - Date/time handling
- threading - Multi-threading
- xml.etree.ElementTree - XML parsing

---

## 🚀 Installation Methods

### Method 1: Automated Install (Recommended)

#### macOS/Linux:
```bash
chmod +x install.sh
./install.sh
```

#### Windows:
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Method 2: Using requirements.txt

```bash
# Install all dependencies
pip install -r requirements.txt

# Or if using pip3
pip3 install -r requirements.txt

# macOS with Homebrew Python
pip3 install --user -r requirements.txt
```

### Method 3: Manual Installation

```bash
pip install requests schedule
```

---

## 🔧 Installation Scripts

### install.sh (macOS/Linux)

**Features:**
- ✅ Automatic Python detection
- ✅ Automatic pip detection
- ✅ Platform-specific handling
- ✅ Upgrades pip automatically
- ✅ Verifies installation
- ✅ Colored output

**Usage:**
```bash
./install.sh
```

**What it does:**
1. Checks for Python 3.7+
2. Checks for pip
3. Upgrades pip to latest
4. Installs dependencies from requirements.txt
5. Verifies installation
6. Reports success/failure

### install.ps1 (Windows)

**Features:**
- ✅ PowerShell native
- ✅ Colored output
- ✅ Windows-specific paths
- ✅ Error handling

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

---

## 📋 requirements.txt

```txt
# Vopak Alert - Python Dependencies
requests>=2.31.0
schedule>=1.2.0
```

**Install:**
```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### Issue: "externally-managed-environment"

**macOS with Homebrew Python:**
```bash
# Use --user flag
pip3 install --user -r requirements.txt

# Or use --break-system-packages
pip3 install --break-system-packages -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "tkinter not found"

**macOS:**
```bash
# Install tkinter via Homebrew
brew install python-tk

# Or reinstall Python with tkinter
brew reinstall python@3.13
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

### Issue: "pip not found"

**Install pip:**
```bash
# macOS
python3 -m ensurepip --upgrade

# Linux
sudo apt-get install python3-pip

# Windows
python -m ensurepip --upgrade
```

### Issue: Permission Denied

```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

---

## ✅ Verify Installation

### Check if packages are installed:

```bash
pip list | grep -E "(requests|schedule)"
```

**Expected output:**
```
requests    2.31.0
schedule    1.2.0
```

### Test the application:

```bash
python3 main.py
```

Should show GUI window with no import errors.

---

## 🔍 What Gets Installed

### requests library
- **Purpose:** HTTP library for API calls
- **Used for:** 
  - Calling Vopak Boiler Activity API
  - Checking Production Status
  - Getting OPC Data
- **Website:** https://docs.python-requests.org/

### schedule library
- **Purpose:** Job scheduling for Python
- **Used for:** Running monitoring tasks periodically
- **Website:** https://schedule.readthedocs.io/

---

## 📦 Installation Locations

### System-wide installation:
```
/usr/local/lib/python3.x/site-packages/
```

### User installation (--user):
```
~/.local/lib/python3.x/site-packages/
```

### Virtual environment:
```
venv/lib/python3.x/site-packages/
```

---

## 🚀 After Installation

### 1. Verify Installation:
```bash
python3 -c "import requests; import schedule; print('OK')"
```

### 2. Run the Application:
```bash
python3 main.py
```

### 3. Build Executable (Optional):
```bash
./build.sh          # or
python3 build.py    # or
./build_macos.sh    # macOS only
```

---

## 📝 File Structure

```
vopakalert/
├── requirements.txt      # Dependencies list
├── install.sh            # Install script (macOS/Linux)
├── install.ps1           # Install script (Windows)
├── main.py               # Main application
└── lib.py                # Utility functions
```

---

## ✨ Quick Start

```bash
# 1. Clone/download project
cd vopakalert

# 2. Install dependencies
./install.sh

# 3. Run application
python3 main.py

# 4. (Optional) Build executable
./build_macos.sh
```

---

**Status:** ✅ Installation scripts ready!

