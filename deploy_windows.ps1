# BSM Windows PowerShell Deployment Script
# This script downloads and sets up BSM from GitHub
# Run this script in PowerShell as Administrator for best results

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BSM - BullShit Meter Windows Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Download BSM from GitHub" -ForegroundColor White
Write-Host "  2. Set up Python virtual environment" -ForegroundColor White
Write-Host "  3. Install all dependencies" -ForegroundColor White
Write-Host "  4. Create desktop shortcuts" -ForegroundColor White
Write-Host "  5. Launch BSM" -ForegroundColor White
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
    $hasGit = $true
} catch {
    Write-Host "⚠️  WARNING: Git is not installed" -ForegroundColor Yellow
    Write-Host "You can install Git from https://git-scm.com" -ForegroundColor Yellow
    Write-Host "Or download BSM manually from:" -ForegroundColor Yellow
    Write-Host "https://github.com/ChrisNelsonOK/BSM-BullShit-Meter" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Continuing without Git..." -ForegroundColor Yellow
    $hasGit = $false
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Download BSM from GitHub
Write-Host ""
if ($hasGit) {
    Write-Host "Downloading BSM from GitHub..." -ForegroundColor Yellow
    
    if (Test-Path "BSM-BullShit-Meter") {
        Write-Host "Removing existing BSM folder..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "BSM-BullShit-Meter"
    }
    
    try {
        git clone https://github.com/ChrisNelsonOK/BSM-BullShit-Meter.git
        Set-Location "BSM-BullShit-Meter"
        Write-Host "✓ BSM downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to clone repository" -ForegroundColor Red
        Write-Host "Please check your internet connection or download manually" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Skipping Git clone - assuming manual download" -ForegroundColor Yellow
    if (-not (Test-Path "BSM-BullShit-Meter")) {
        Write-Host "❌ BSM-BullShit-Meter folder not found" -ForegroundColor Red
        Write-Host "Please download from: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location "BSM-BullShit-Meter"
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
try {
    python -m venv bsm_env
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and install packages
Write-Host ""
Write-Host "Installing BSM requirements..." -ForegroundColor Yellow

$activateScript = ".\bsm_env\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    # Activate virtual environment
    & $activateScript
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    # Install Windows-specific packages
    pip install pywin32 pyinstaller
    
    Write-Host "✓ All packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find activation script" -ForegroundColor Red
    exit 1
}

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow

$desktopPath = [Environment]::GetFolderPath("Desktop")
$bsmPath = Get-Location
$shortcutPath = Join-Path $desktopPath "BSM - BullShit Meter.lnk"

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = Join-Path $bsmPath "bsm_env\Scripts\python.exe"
$Shortcut.Arguments = "-m bsm.main"
$Shortcut.WorkingDirectory = $bsmPath
$Shortcut.IconLocation = Join-Path $bsmPath "bsm_env\Scripts\python.exe"
$Shortcut.Description = "BSM - BullShit Meter AI Fact Checker"
$Shortcut.Save()

Write-Host "✓ Desktop shortcut created" -ForegroundColor Green

# Create batch launcher
Write-Host ""
Write-Host "Creating launcher script..." -ForegroundColor Yellow

$launcherContent = @"
@echo off
cd /d "$bsmPath"
call bsm_env\Scripts\activate.bat
python -m bsm.main
pause
"@

$launcherContent | Out-File -FilePath "launch_bsm.bat" -Encoding ASCII
Write-Host "✓ Launcher script created" -ForegroundColor Green

# Test installation
Write-Host ""
Write-Host "Testing BSM installation..." -ForegroundColor Yellow

try {
    python -c "import bsm.main; print('✓ BSM imports successfully')"
    Write-Host "✓ BSM installation test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ BSM failed to import - check error messages above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ BSM DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "BSM has been successfully deployed on Windows!" -ForegroundColor Green
Write-Host "Downloaded from: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 HOW TO RUN BSM:" -ForegroundColor Cyan
Write-Host "  1. Double-click 'BSM - BullShit Meter' on your Desktop" -ForegroundColor White
Write-Host "  2. Or run: launch_bsm.bat" -ForegroundColor White
Write-Host "  3. Or manually activate environment and run python -m bsm.main" -ForegroundColor White
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Configure AI providers in Settings (OpenAI, Claude, or Ollama)" -ForegroundColor White
Write-Host "  2. Set up global hotkeys for quick access" -ForegroundColor White
Write-Host "  3. Test screenshot capture and AI analysis" -ForegroundColor White
Write-Host ""
Write-Host "🔧 TROUBLESHOOTING:" -ForegroundColor Cyan
Write-Host "  - If hotkeys don't work, run as Administrator" -ForegroundColor White
Write-Host "  - For Ollama: Install from https://ollama.ai" -ForegroundColor White
Write-Host "  - Check Windows Defender/Antivirus settings" -ForegroundColor White
Write-Host "  - For updates: git pull in the BSM folder" -ForegroundColor White
Write-Host ""

$launch = Read-Host "Would you like to launch BSM now? (y/n)"
if ($launch -eq "y" -or $launch -eq "Y" -or $launch -eq "yes") {
    Write-Host "Launching BSM..." -ForegroundColor Yellow
    Start-Process -FilePath "launch_bsm.bat" -WorkingDirectory $bsmPath
    Write-Host ""
    Write-Host "BSM is now running! Check your system tray." -ForegroundColor Green
}

Write-Host ""
Write-Host "Deployment complete! 🎉" -ForegroundColor Green
Read-Host "Press Enter to exit"
