@echo off
echo Building Vopak Monitor for Windows...
echo.

REM Kill any running instances
echo Checking for running instances...
taskkill /F /IM main.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 1 /nobreak >nul

REM Clean build directories
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist\main.exe del /f /q dist\main.exe

REM Build with PyInstaller
echo Building executable...
python -m PyInstaller --clean --noconfirm main.spec

echo.
echo Build complete! Check dist\main.exe

