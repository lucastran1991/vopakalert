# Quick Start: Building macOS App

## 🚀 Fast Track (3 Commands)

### 1. Install Dependencies
```bash
pip3 install pyinstaller requests schedule
```

### 2. Build the App
```bash
./build_macos.sh
# or
python3 build.py
```

### 3. Run the App
```bash
open dist/VopakAlert_*.app
```

---

## 📦 What You'll Get

```
dist/VopakAlert_[timestamp].app
```

**Features:**
- ✅ Double-clickable macOS app
- ✅ No Python installation needed
- ✅ All dependencies included
- ✅ Works on any Mac (ARM64/Intel)

---

## 🎯 Build Options

### Option 1: Use build_macos.sh (Recommended)
```bash
./build_macos.sh
```
- Creates proper .app bundle
- macOS-specific optimizations
- Clean output

### Option 2: Use build.py (Cross-platform)
```bash
python3 build.py
```
- Works on any OS
- Timestamp in filename
- Auto-detects platform

### Option 3: Manual PyInstaller
```bash
pyinstaller --windowed --onedir --name "VopakAlert" main.py
```

---

## 📝 Current Project Status

### What Already Works:
✅ You already have built app bundles in `dist/`
✅ The build scripts are configured for macOS
✅ One-click building with scripts

### How to Build Fresh:

```bash
# Clean
rm -rf build dist

# Build
python3 build.py

# Output
# dist/main_[timestamp].app
```

---

## 🎨 Optional: Add App Icon

1. Create or download icon file (`icon.icns`)
2. Add to build command:
```bash
pyinstaller --windowed --onedir --name "VopakAlert" --icon=icon.icns main.py
```

---

## ❓ Troubleshooting

### Can't open app?
```bash
# Allow from unidentified developer
xattr -cr "VopakAlert.app"
```

### App too large?
Normal! ~30-100MB including Python + dependencies.

### GUI not working?
Check if tkinter is properly bundled. The warning is normal.

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Build script runs successfully
- [ ] App opens in Finder
- [ ] App runs without errors
- [ ] GUI displays correctly
- [ ] Can select tasks
- [ ] Can toggle email alerts
- [ ] Can start/stop monitoring
- [ ] Logs display properly

---

## 📚 More Info

- **Full Guide:** See `BUILD_MACOS.md`
- **General Build:** See `README.md`
- **Project Analysis:** See `ANALYSIS.md`

---

**That's it! 🎉**

Your macOS app is ready when you run:
```bash
./build_macos.sh
```

