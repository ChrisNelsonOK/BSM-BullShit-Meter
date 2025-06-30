@echo off
REM BSM One-Click Installer - Download and run this script to install BSM
REM Download from: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter/raw/main/install_bsm.bat

echo ========================================
echo BSM - BullShit Meter One-Click Installer
echo ========================================
echo.
echo This installer will:
echo   1. Download BSM from GitHub
echo   2. Set up Python virtual environment  
echo   3. Install all dependencies
echo   4. Create desktop shortcuts
echo   5. Launch BSM
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git is not installed
    echo Please install Git from https://git-scm.com
    echo Or download BSM ZIP manually from:
    echo https://github.com/ChrisNelsonOK/BSM-BullShit-Meter
    echo.
    pause
    exit /b 1
)

echo ✓ Git found
git --version

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Download BSM from GitHub
echo.
echo Downloading BSM from GitHub...
if exist "BSM-BullShit-Meter" (
    echo Removing existing BSM folder...
    rmdir /s /q "BSM-BullShit-Meter"
)

git clone https://github.com/ChrisNelsonOK/BSM-BullShit-Meter.git
if %errorlevel% neq 0 (
    echo ERROR: Failed to clone repository
    echo Please check your internet connection
    pause
    exit /b 1
)

cd BSM-BullShit-Meter
echo ✓ BSM downloaded successfully

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv bsm_env
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call bsm_env\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing BSM requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

REM Install additional Windows-specific packages
echo.
echo Installing Windows-specific packages...
pip install pywin32 pyinstaller

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set BSM_PATH=%CD%
set SHORTCUT_PATH=%DESKTOP%\BSM - BullShit Meter.lnk

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%BSM_PATH%\bsm_env\Scripts\python.exe'; $Shortcut.Arguments = '-m bsm.main'; $Shortcut.WorkingDirectory = '%BSM_PATH%'; $Shortcut.IconLocation = '%BSM_PATH%\bsm_env\Scripts\python.exe'; $Shortcut.Description = 'BSM - BullShit Meter AI Fact Checker'; $Shortcut.Save()"

REM Create batch launcher
echo.
echo Creating launcher script...
echo @echo off > launch_bsm.bat
echo cd /d "%BSM_PATH%" >> launch_bsm.bat
echo call bsm_env\Scripts\activate.bat >> launch_bsm.bat
echo python -m bsm.main >> launch_bsm.bat
echo pause >> launch_bsm.bat

REM Test the installation
echo.
echo Testing BSM installation...
python -c "import bsm.main; print('✓ BSM imports successfully')"
if %errorlevel% neq 0 (
    echo ERROR: BSM failed to import
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ BSM INSTALLATION SUCCESSFUL!
echo ========================================
echo.
echo BSM has been successfully installed!
echo Downloaded from: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter
echo.
echo 🚀 HOW TO RUN BSM:
echo   1. Double-click "BSM - BullShit Meter" on your Desktop
echo   2. Or run: launch_bsm.bat
echo   3. Or manually: bsm_env\Scripts\activate.bat then python -m bsm.main
echo.
echo 📋 NEXT STEPS:
echo   1. Configure AI providers in Settings (OpenAI, Claude, or Ollama)
echo   2. Set up global hotkeys for quick access
echo   3. Test screenshot capture and AI analysis
echo.
echo 🔧 TROUBLESHOOTING:
echo   - If hotkeys don't work, run as Administrator
echo   - For Ollama: Install from https://ollama.ai
echo   - Check Windows Defender/Antivirus settings
echo   - For updates: git pull in the BSM folder
echo.
echo Press any key to launch BSM now...
pause >nul

REM Launch BSM
echo Launching BSM...
start "" "%BSM_PATH%\launch_bsm.bat"

echo.
echo BSM is now running! Check your system tray.
echo.
pause