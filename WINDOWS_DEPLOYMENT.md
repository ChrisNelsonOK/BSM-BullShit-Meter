# 🚀 BSM Windows Deployment Guide

## 📋 **Prerequisites**

### Required Software
1. **Python 3.8+** - Download from [python.org](https://python.org)
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
2. **Git** (recommended) - For downloading BSM from [git-scm.com](https://git-scm.com)
3. **Windows 10/11** - Tested on modern Windows versions
4. **Internet connection** - For downloading BSM and dependencies

### Optional (for full AI functionality)
- **Ollama** - Local AI models from [ollama.ai](https://ollama.ai)
- **OpenAI API Key** - For GPT models
- **Claude API Key** - For Anthropic models

## 🎯 **One-Click Deployment**

### Method 1: One-Click Deployment (Recommended)
1. **Download the deployment script** from GitHub:
   - Go to: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter
   - Download `deploy_windows.bat` or `deploy_windows.ps1`
2. **Create a new folder** for BSM (e.g., `C:\BSM`)
3. **Place the script** in that folder
4. **Run as Administrator** (recommended for hotkeys):
   - **Batch**: Right-click `deploy_windows.bat` → "Run as administrator"
   - **PowerShell**: Right-click `deploy_windows.ps1` → "Run with PowerShell"
5. **Follow the prompts** - the script will:
   - Check Python and Git installation
   - Download BSM from GitHub automatically
   - Create virtual environment
   - Install all dependencies
   - Create desktop shortcut
   - Test the installation
   - Launch BSM

### Method 2: Manual Installation
If the automated script fails, follow these manual steps:

```cmd
# 1. Clone BSM from GitHub
git clone https://github.com/ChrisNelsonOK/BSM-BullShit-Meter.git
cd BSM-BullShit-Meter

# 2. Create virtual environment
python -m venv bsm_env

# 3. Activate virtual environment
bsm_env\Scripts\activate.bat

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install requirements
pip install -r requirements.txt

# 6. Install Windows-specific packages
pip install pywin32

# 7. Test installation
python -c "import bsm.main; print('BSM ready!')"

# 8. Launch BSM
python -m bsm.main
```

### Method 3: Download ZIP (No Git)
If you don't have Git installed:

1. **Download ZIP**: Go to https://github.com/ChrisNelsonOK/BSM-BullShit-Meter
2. **Click "Code" → "Download ZIP"**
3. **Extract** to your desired folder
4. **Follow manual installation steps** above (skip step 1)

## 🎮 **Running BSM**

### Option 1: Desktop Shortcut
- Double-click **"BSM - BullShit Meter"** on your Desktop

### Option 2: Batch Launcher
- Double-click **`launch_bsm.bat`** in the project folder

### Option 3: Command Line
```cmd
cd C:\path\to\BSM-BullShit-Meter-Utility
bsm_env\Scripts\activate.bat
python -m bsm.main
```

## ⚙️ **Initial Configuration**

### 1. Configure AI Providers
1. **Open BSM Settings** (⚙️ button)
2. **Go to "AI Providers" tab**
3. **Choose your preferred setup**:

   **Option A: Local Ollama (Recommended)**
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull a model: `ollama pull llama3.2`
   - Set Default Provider to "ollama"

   **Option B: OpenAI**
   - Get API key from [platform.openai.com](https://platform.openai.com)
   - Enter API key in settings
   - Set Default Provider to "openai"

   **Option C: Claude**
   - Get API key from [console.anthropic.com](https://console.anthropic.com)
   - Enter API key in settings
   - Set Default Provider to "claude"

### 2. Set Up Hotkeys (Optional)
1. **Run BSM as Administrator** (for global hotkeys)
2. **Open Settings** → "Hotkeys" tab
3. **Configure global hotkey** (default: Ctrl+Shift+B)
4. **Test hotkey functionality**

### 3. Test Core Features
1. **Screenshot Capture**: Click "📷 Capture Screenshot"
2. **Select text region** with mouse drag
3. **AI Analysis**: Click "Analyze Now" when prompted
4. **View Results**: Check the popup window with AI analysis

## 🔧 **Troubleshooting**

### Common Issues

**❌ "Git not found" or "Failed to clone repository"**
- Install Git from [git-scm.com](https://git-scm.com)
- Or download ZIP manually from GitHub
- Check internet connection

**❌ "Python not found"**
- Reinstall Python with "Add to PATH" checked
- Restart Command Prompt after installation

**❌ "Permission denied" or hotkeys not working**
- Run Command Prompt as Administrator
- Run BSM as Administrator for global hotkeys

**❌ "No AI providers available"**
- Configure at least one AI provider in Settings
- For Ollama: Ensure service is running (`ollama serve`)
- For APIs: Check internet connection and API keys

**❌ "Screenshot capture not working"**
- Check Windows permissions for screen capture
- Try running as Administrator
- Ensure no other screen capture tools are interfering

**❌ "Import errors" or "Module not found"**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

### Windows-Specific Notes

**🛡️ Windows Defender**
- May flag BSM as unknown software
- Add BSM folder to exclusions if needed

**🔑 Global Hotkeys**
- Require Administrator privileges
- May conflict with other applications
- Can be disabled in Settings if problematic

**📱 System Tray**
- BSM runs in system tray when window is closed
- Right-click tray icon for options
- Use "Quit BSM" to fully exit

## 🎯 **Performance Tips**

### For Best Performance
1. **Use Ollama locally** - Faster than API calls
2. **Run as Administrator** - Better hotkey reliability
3. **Close other screen capture tools** - Avoid conflicts
4. **Use SSD storage** - Faster model loading

### Resource Usage
- **RAM**: ~200-500MB (depending on AI model)
- **CPU**: Low when idle, moderate during AI analysis
- **Network**: Only for API-based AI providers
- **Storage**: ~50MB + AI models (if using Ollama)

## 🚀 **Advanced Setup**

### Creating Windows Service (Optional)
For automatic startup, you can create a Windows service:

```cmd
# Install service wrapper
pip install pywin32

# Create service (run as Administrator)
python -m win32serviceutil install bsm.main
```

### Building Standalone Executable
To create a single .exe file:

```cmd
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico bsm/main.py

# Find executable in dist/ folder
```

## 📞 **Support**

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all prerequisites are installed
3. Try running as Administrator
4. Check Windows Event Viewer for errors
5. Review BSM logs in the application folder

---

**🎉 Enjoy using BSM - Your AI-powered fact-checking companion!**
