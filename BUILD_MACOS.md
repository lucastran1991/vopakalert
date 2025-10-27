# Building macOS Application for Vopak Alert

## 🍎 Overview

The project can be built into a macOS `.app` bundle that can be run natively on macOS without requiring Python or dependencies to be installed.

## 📦 What You Get

After building, you'll have:
- **`.app` bundle** - A double-clickable macOS application
- **Standalone** - No Python installation required
- **All dependencies included** - Bundled inside the app

## 🚀 Build Methods

### Method 1: Using build.py (Recommended)

```bash
python3 build.py
```

This will automatically:
- Detect macOS platform
- Create `.app` bundle
- Add timestamp to filename
- Output: `dist/main_[timestamp].app`

### Method 2: Using build.sh

```bash
./build.sh
```

### Method 3: Manual PyInstaller

```bash
# Basic build
pyinstaller --windowed --onefile main.py

# Or create .app bundle explicitly
pyinstaller --windowed --onedir --name "VopakAlert" main.py
```

---

## 📋 Prerequisites

### 1. Install Python 3.7+

```bash
# Check Python version
python3 --version

# Install via Homebrew if needed
brew install python3
```

### 2. Install PyInstaller

```bash
pip3 install --break-system-packages pyinstaller
# or
pip3 install pyinstaller
```

### 3. Install Project Dependencies

```bash
pip3 install requests schedule
```

---

## 🔨 Build Process Explained

### Step-by-Step Build

#### 1. Clean Previous Builds (Optional)

```bash
rm -rf build dist
```

#### 2. Build the Application

**Option A: Single File Executable**
```bash
pyinstaller --windowed --onefile main.py
# Creates: dist/main
```

**Option B: App Bundle (Recommended)**
```bash
pyinstaller --windowed --onedir --name "VopakAlert" main.py
# Creates: dist/VopakAlert.app
```

**Option C: With Custom Icon**
```bash
# First create or download an .icns file
pyinstaller --windowed --onedir --name "VopakAlert" \
  --icon=icon.icns main.py
```

---

## 📁 App Bundle Structure

A macOS `.app` bundle has this structure:

```
VopakAlert.app/
└── Contents/
    ├── Info.plist          # App metadata
    ├── MacOS/
    │   └── VopakAlert      # Executable
    ├── Resources/
    │   └── icon-windowed.icns
    └── Frameworks/         # Dependencies
        └── Python libraries
```

---

## ⚙️ Advanced Configuration

### Creating a Custom Icon

1. **Convert PNG to ICNS:**
```bash
# Install iconutil (comes with macOS)
iconutil -c icns icon.iconset

# Or use online converter
# https://cloudconvert.com/png-to-icns
```

2. **Structure for .iconset:**
```
icon.iconset/
├── icon_16x16.png
├── icon_16x16@2x.png
├── icon_32x32.png
├── icon_32x32@2x.png
├── icon_128x128.png
├── icon_128x128@2x.png
├── icon_256x256.png
├── icon_256x256@2x.png
├── icon_512x512.png
└── icon_512x512@2x.png
```

3. **Build with icon:**
```bash
pyinstaller --windowed --onedir --name "VopakAlert" \
  --icon=icon.icns main.py
```

---

## 🎯 PyInstaller Options for macOS

### Common Options:

| Option | Description |
|--------|-------------|
| `--windowed` | No console window (use `-w` shorthand) |
| `--onedir` | Create directory app (recommended for macOS) |
| `--onefile` | Single executable (Windows-like) |
| `--name` | App name (default: main) |
| `--icon` | Custom .icns icon file |
| `--clean` | Clean cache before building |
| `--noconfirm` | Overwrite output without asking |

### Example:

```bash
pyinstaller \
  --windowed \
  --onedir \
  --name "VopakAlert" \
  --icon=icon.icns \
  --clean \
  --noconfirm \
  main.py
```

---

## 🐛 Troubleshooting

### Issue: "tkinter installation is broken"

This warning appears but the app still works:
```
WARNING: tkinter installation is broken
```

**Solution:** The app will run but GUI may have issues. Check app logs:
```bash
# Run from Terminal to see errors
open -a "VopakAlert.app"
```

### Issue: App Won't Open

**Gatekeeper Error:**
```bash
# This app can't be opened because it's from an unidentified developer
```

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr "VopakAlert.app"

# Or allow from System Preferences
# System Preferences > Security & Privacy > General
```

### Issue: Missing Dependencies

If the app crashes, check Console:
```bash
# View logs
log show --predicate 'process == "VopakAlert"' --last 5m
```

### Issue: Too Large App Size

App bundles are typically 30-100MB because they include Python + libraries.

**Reduce size:**
```bash
# Exclude unused modules
pyinstaller --windowed --onedir \
  --exclude-module matplotlib \
  --exclude-module numpy \
  main.py
```

---

## 📤 Distributing Your App

### 1. Create DMG (Disk Image)

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Vopak Alert" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 185 \
  "VopakAlert.dmg" \
  "dist/VopakAlert.app"
```

### 2. Code Signing (Optional)

```bash
# Sign app (requires Developer ID)
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "VopakAlert.app"

# Verify signature
codesign --verify --deep --strict --verbose=2 "VopakAlert.app"
```

### 3. Notarize (Optional, for Gatekeeper)

```bash
# Create zip for notarization
ditto -c -k --keepParent "VopakAlert.app" "VopakAlert.zip"

# Submit for notarization
xcrun altool --notarize-app \
  --primary-bundle-id "com.atomiton.vopakalert" \
  --username "your@appleid.com" \
  --password "app-specific-password" \
  --file "VopakAlert.zip"
```

---

## ✅ Testing the App

### Run from Terminal:

```bash
# Run the executable inside app
./dist/VopakAlert.app/Contents/MacOS/VopakAlert

# Or double-click in Finder
open dist/VopakAlert.app
```

### Verify It Works:

1. **Open the app** - Should show GUI window
2. **Check task selection** - All 3 checkboxes visible
3. **Toggle email** - Checkbox works
4. **Start monitoring** - Click Start button
5. **View logs** - See log messages

---

## 📝 Current Build Output

Your current build creates:
```
dist/
├── main_[timestamp]          # Executable (7.6MB)
└── main_[timestamp].app/    # App bundle
    └── Contents/
        ├── Info.plist
        ├── MacOS/main_[timestamp]
        └── Resources/
```

---

## 🎯 Quick Reference

### Build Command:
```bash
python3 build.py
```

### Output:
- **Location:** `dist/main_[timestamp].app`
- **Size:** ~7.6MB executable + app bundle
- **Format:** macOS .app bundle

### Run:
```bash
open dist/main_[timestamp].app
```

---

## 🔄 What Gets Included

The built app includes:
- ✅ Python runtime
- ✅ tkinter (GUI)
- ✅ requests (API calls)
- ✅ schedule (Task scheduling)
- ✅ smtplib (Email)
- ✅ All dependencies

**Everything bundled - no installation needed!**

---

**Happy Building! 🚀**

