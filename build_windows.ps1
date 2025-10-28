# Building Vopak Monitor for Windows
Write-Host "Building Vopak Monitor for Windows..." -ForegroundColor Cyan
Write-Host ""

# Kill any running instances
Write-Host "Checking for running instances..."
Get-Process | Where-Object {$_.ProcessName -like "*main*" -or $_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Clean build directories
Write-Host "Cleaning previous builds..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\main.exe") { Remove-Item -Force "dist\main.exe" }

# Build with PyInstaller
Write-Host "Building executable..."
python -m PyInstaller --clean --noconfirm main.spec

Write-Host ""
Write-Host "Build complete! Check dist\main.exe" -ForegroundColor Green

