# Numen Installation Script for Windows
Write-Host "Installing Numen - AI-Augmented Terminal Notepad" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check Python version
try {
    $pythonVersionOutput = python --version 2>&1
    if ($pythonVersionOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
        $versionMajor = [int]$Matches[1]
        $versionMinor = [int]$Matches[2]
        $versionNum = $versionMajor * 100 + $versionMinor
        
        Write-Host "Python version: $versionMajor.$versionMinor" -ForegroundColor Green
        
        if ($versionNum -lt 311) {
            Write-Host "Error: Numen requires Python 3.11 or newer" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Error: Unable to determine Python version" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Python not found. Please install Python 3.11 or newer" -ForegroundColor Red
    exit 1
}

# Create config directories
$numenHome = "$env:USERPROFILE\.numen"
$notesDir = "$numenHome\notes"
$cacheDir = "$numenHome\cache"
$logsDir = "$numenHome\logs"

# Check if pipx is installed
$pipxInstalled = $null -ne (Get-Command pipx -ErrorAction SilentlyContinue)

if ($pipxInstalled) {
    Write-Host "pipx found, using isolated installation (recommended)" -ForegroundColor Green
    
    # Check if already installed with pipx
    $numenInstalled = (pipx list) -match "numen"
    
    if ($numenInstalled) {
        Write-Host "Numen already installed with pipx, upgrading..." -ForegroundColor Yellow
        pipx install . --force
    } else {
        Write-Host "Installing Numen with pipx..." -ForegroundColor Green
        pipx install .
    }
    
    # Create config directory if it doesn't exist
    if (-not (Test-Path $numenHome)) {
        Write-Host "Setting up configuration..." -ForegroundColor Green
        New-Item -ItemType Directory -Path $notesDir, $cacheDir, $logsDir -Force | Out-Null
    }
    
    Write-Host "Installation complete! Run 'numen --help' to get started." -ForegroundColor Green
} else {
    Write-Host "pipx not found, falling back to traditional pip installation" -ForegroundColor Yellow
    Write-Host "NOTE: For better isolation, consider installing pipx: https://pypa.github.io/pipx/" -ForegroundColor Yellow
    
    # Install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Green
    pip install -e .
    
    # Create config directory
    Write-Host "Setting up configuration..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $notesDir, $cacheDir, $logsDir -Force | Out-Null
    
    # Run numen for the first time to generate config
    Write-Host "Generating initial configuration..." -ForegroundColor Green
    python -c "from numen.config import ensure_config_exists; ensure_config_exists()"
    
    Write-Host "Installation complete! Run 'numen --help' to get started." -ForegroundColor Green
}

# Add the Scripts directory to PATH if it's not already there
$scriptsPath = ""
if ($pipxInstalled) {
    # For pipx installations
    $scriptsPath = "$env:LOCALAPPDATA\pipx\venvs\numen\Scripts"
} else {
    # For regular pip installations
    $scriptsPath = (python -c "import site; print(site.getusersitepackages())").Trim() -replace "site-packages", "Scripts"
}

if ($scriptsPath -and (Test-Path $scriptsPath)) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($userPath -notlike "*$scriptsPath*") {
        Write-Host "Adding Numen to your PATH..." -ForegroundColor Yellow
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsPath", "User")
        Write-Host "PATH updated. You'll need to restart your terminal for the 'numen' command to work." -ForegroundColor Yellow
    } else {
        Write-Host "Numen is already in your PATH." -ForegroundColor Green
    }
} else {
    Write-Host "Warning: Could not determine the Scripts directory to add to PATH." -ForegroundColor Red
    Write-Host "You may need to manually add the directory containing numen.exe to your PATH." -ForegroundColor Red
}

Write-Host ""
Write-Host "Notes are stored in: $notesDir" -ForegroundColor Cyan
Write-Host "Edit config with: numen config" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== IMPORTANT ===" -ForegroundColor Yellow
Write-Host "You need to restart your terminal for the 'numen' command to be available." -ForegroundColor Yellow
Write-Host "After restarting, type 'numen --help' to get started." -ForegroundColor Yellow
