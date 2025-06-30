# BSM Windows Deployment Guide

## Quick Installation (Recommended)

### Option 1: One-Click Installer
1. Download the installer script: [install_bsm.bat](https://github.com/ChrisNelsonOK/BSM-BullShit-Meter/raw/main/install_bsm.bat)
2. Right-click and "Run as Administrator" (for hotkey support)
3. Follow the prompts - everything is automated!

### Option 2: Enhanced Deployment Scripts
- **Batch Script**: [deploy_windows.bat](deploy_windows.bat)
- **PowerShell Script**: [deploy_windows.ps1](deploy_windows.ps1)

## Manual Installation

### Prerequisites
1. **Python 3.8+** from [python.org](https://python.org)
   - ✅ Check "Add Python to PATH" during installation
2. **Git** from [git-scm.com](https://git-scm.com) (optional but recommended)

### Installation Steps

1. **Download BSM**
   ```cmd
   git clone https://github.com/ChrisNelsonOK/BSM-BullShit-Meter.git
   cd BSM-BullShit-Meter
   ```
   
   Or download ZIP from GitHub and extract.

2. **Create Virtual Environment**
   ```cmd
   python -m venv bsm_env
   bsm_env\Scripts\activate.bat
   ```

3. **Install Dependencies**
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install pywin32 pyinstaller
   ```

4. **Run BSM**
   ```cmd
   python -m bsm.main
   ```

## Configuration

### AI Providers
1. **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com)
2. **Claude**: Get API key from [console.anthropic.com](https://console.anthropic.com)
3. **Ollama**: Install from [ollama.ai](https://ollama.ai) for local AI

### Settings Location
- User settings: `%USERPROFILE%\.bsm\settings.yaml`
- API keys: Encrypted in `%USERPROFILE%\.bsm\.key`
- Database: `%USERPROFILE%\.bsm\bsm_history.db`

## Features

### Core Functionality
- 📸 **Screenshot Capture**: Regional OCR text extraction
- 🤖 **AI Analysis**: Multi-provider fact-checking (OpenAI, Claude, Ollama)
- 📋 **Results Display**: Beautiful markdown-formatted popup windows
- ⚡ **Global Hotkeys**: Quick access from anywhere
- 🎯 **System Tray**: Persistent background operation

### AI Attitude Modes
- **Argumentative**: Aggressive fact-checking and counter-arguments
- **Balanced**: Fair analysis considering multiple perspectives
- **Helpful**: Constructive and educational responses

## Troubleshooting

### Common Issues

**Hotkeys not working:**
- Run BSM as Administrator
- Check Windows security settings
- Verify hotkey combinations aren't used by other apps

**AI providers failing:**
- Verify API keys in Settings
- Check internet connection
- For Ollama: Ensure service is running (`ollama serve`)

**Screenshot capture issues:**
- Check screen permissions
- Disable conflicting screenshot tools
- Try different screen regions

**Import errors:**
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version`
- Verify virtual environment activation

### Windows Defender
If Windows Defender blocks BSM:
1. Add BSM folder to exclusions
2. Allow Python.exe through firewall
3. Temporarily disable real-time protection during installation

### Updates
```cmd
cd BSM-BullShit-Meter
git pull origin main
pip install -r requirements.txt --upgrade
```

## Advanced Configuration

### Custom Hotkeys
Edit settings or use the Settings UI:
- Global analysis: `Ctrl+Shift+B` (default)
- Screenshot capture: `Ctrl+Shift+S`
- Attitude mode cycling: `Ctrl+Shift+A`

### Database Management
- History stored in SQLite database
- Automatic backups in `.bsm` folder
- Export/import functionality in Settings

### Privacy & Security
- All data stored locally
- API keys encrypted with Fernet
- No telemetry or data sharing
- User settings never included in version control

## Building Standalone Executable

```cmd
pyinstaller bsm.spec
```

Executable will be in `dist/` folder.

## Support

- **GitHub Issues**: [Report bugs](https://github.com/ChrisNelsonOK/BSM-BullShit-Meter/issues)
- **Documentation**: Check README.md for detailed usage
- **Updates**: Star the repo for notifications

---

**BSM - BullShit Meter**: AI-powered fact-checking and counter-argument generation tool.

Repository: https://github.com/ChrisNelsonOK/BSM-BullShit-Meter