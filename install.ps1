# Vopak Alert - Installation Script (PowerShell)
# Installs required Python dependencies on Windows

Write-Host "==================================================" -ForegroundColor Blue
Write-Host "  VOPAK ALERT - DEPENDENCY INSTALLATION" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue
Write-Host ""

# Function to check Python
function Test-Python {
    Write-Host "🔨 Checking Python..." -ForegroundColor Blue
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        return $true
    }
    elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonVersion = python3 --version
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "❌ Python is not installed!" -ForegroundColor Red
        Write-Host "Please install Python 3.7 or higher from:" -ForegroundColor Yellow
        Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
}

# Function to check pip
function Test-Pip {
    Write-Host "🔨 Checking pip..." -ForegroundColor Blue
    
    $pipCmd = $null
    
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        $pipCmd = "pip"
    }
    elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
        $pipCmd = "pip3"
    }
    
    if ($pipCmd) {
        $pipVersion = & $pipCmd --version
        Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
        return $pipCmd
    }
    else {
        Write-Host "❌ pip is not installed!" -ForegroundColor Red
        return $null
    }
}

# Main installation
if (-not (Test-Python)) {
    Write-Host ""
    Write-Host "Installation aborted." -ForegroundColor Red
    exit 1
}

Write-Host ""

$pipCmd = Test-Pip

if (-not $pipCmd) {
    Write-Host ""
    Write-Host "Installation aborted." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔨 Upgrading pip..." -ForegroundColor Blue
& $pipCmd install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

Write-Host ""

if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
    Write-Host "Please ensure you're in the project directory"
    exit 1
}

Write-Host "🔨 Installing dependencies from requirements.txt..." -ForegroundColor Blue
Write-Host ""

& $pipCmd install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🔨 Verifying installed packages..." -ForegroundColor Blue
    Write-Host ""
    
    & $pipCmd list | Select-String -Pattern "requests|schedule"
    
    Write-Host ""
    Write-Host "✅ Installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the application:" -ForegroundColor Blue
    Write-Host "  python main.py" -ForegroundColor Cyan
    Write-Host ""
}
else {
    Write-Host "❌ Installation failed!" -ForegroundColor Red
    exit 1
}

