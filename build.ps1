# Vopak Alert Build Script (PowerShell)
# Build Python app to exe using PyInstaller

Write-Host "🔨 Building Vopak Alert..." -ForegroundColor Blue

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed!" -ForegroundColor Red
    exit 1
}

# Install PyInstaller if not installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Blue
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the exe
Write-Host "⚙️  Building exe file..." -ForegroundColor Blue
pyinstaller main.spec

# Check if build succeeded
if (Test-Path "dist\main.exe") {
    $fileSize = (Get-Item "dist\main.exe").Length / 1MB
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "📁 Output: dist\main.exe"
    Write-Host "📏 Size: $([math]::Round($fileSize, 2)) MB"
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
