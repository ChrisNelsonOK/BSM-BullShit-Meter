# BSM Installation and Setup Guide

## Quick Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR (required for screenshot analysis):**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **Run BSM:**
   ```bash
   python run.py
   ```

## First-Time Setup

### 1. Grant Accessibility Permissions (macOS)
When you first run BSM on macOS, you'll see a message about accessibility permissions:
```
This process is not trusted! Input event monitoring will not be possible until it is added to accessibility clients.
```

To fix this:
1. Go to **System Preferences > Security & Privacy > Privacy**
2. Select **Accessibility** from the left panel
3. Click the lock icon and enter your password
4. Add your terminal or Python to the allowed applications
5. Restart BSM

### 2. Configure API Keys
1. Right-click the BSM system tray icon
2. Select **Settings**
3. Go to the **API Keys** tab
4. Add your API keys:
   - **OpenAI**: Get from https://platform.openai.com/api-keys
   - **Claude**: Get from https://console.anthropic.com/

### 3. Choose Your AI Provider
1. In Settings, go to the **Behavior** tab
2. Select your preferred **Primary Provider**:
   - **OpenAI**: Uses GPT-4 for analysis
   - **Claude**: Uses Claude-3-Sonnet for analysis
   - **Ollama**: Uses local LLM (requires Ollama to be running)

### 4. Set Your Attitude Mode
Choose how aggressive you want the fact-checking to be:
- **Balanced**: Objective analysis with neutral tone
- **Argumentative**: Aggressive fact-checking, finds flaws
- **Helpful**: Educational tone, constructive feedback

## Usage

### Global Hotkey (Primary Method)
1. Select text anywhere on your screen
2. Press **Ctrl+Shift+B** (or your custom hotkey)
3. BSM analyzes the text and shows results

### System Tray Menu
Right-click the BSM icon in your system tray:
- **Analyze Clipboard**: Analyzes text currently in clipboard
- **Analyze Screenshot**: Takes screenshot and analyzes extracted text
- **Settings**: Opens configuration window
- **Quit**: Exits BSM

### Results Window
- **Copy Results**: Copies the analysis to clipboard
- **Resizable**: Drag corners to resize
- **Position Memory**: Window opens in the same location each time

## Troubleshooting

### "No text selected" Error
- Make sure text is actually selected before pressing the hotkey
- Try using "Analyze Clipboard" instead

### API Errors
- Check that your API keys are correct
- Verify you have sufficient API credits
- Check your internet connection

### Hotkey Not Working
- **macOS**: Grant accessibility permissions (see above)
- **Windows**: Try running as administrator
- **Linux**: Check if another app is using the same hotkey

### OCR Not Working
- Verify Tesseract is installed: `tesseract --version`
- Check the PATH includes Tesseract location
- Try taking a screenshot with clear, readable text

### App Crashes
- Run `python test_complete_functionality.py` to check for issues
- Check the terminal output for error messages
- Ensure all dependencies are installed
- If settings save crashes, try running BSM from terminal to see error details

### Settings Save Issues
- The app now includes better error handling for settings
- API keys are encrypted and saved automatically
- If save fails, check file permissions in `~/.bsm/` directory

## Local LLM Setup (Ollama)

To use local LLMs as a fallback or primary provider:

1. **Install Ollama:**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Download a model:**
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama
   ```

3. **Configure BSM:**
   - Set **Primary Provider** to "ollama" in settings
   - Set **Ollama Endpoint** to "http://localhost:11434"
   - Set **Ollama Model** to your downloaded model name

## Advanced Configuration

### Custom Hotkeys
Format: `modifier+modifier+key`
Examples:
- `ctrl+shift+b` (default)
- `cmd+shift+b` (macOS)
- `alt+f12`
- `ctrl+alt+space`

### Database Location
By default, analysis history is stored in `~/.bsm/bsm_history.db`
You can change this in Settings > Database tab.

### Settings File
Configuration is stored in `~/.bsm/settings.yaml`
API keys are encrypted for security.

## Security Notes

- ✅ API keys are encrypted locally
- ✅ Analysis history stays on your machine
- ✅ No telemetry or data collection
- ✅ Network requests only go to chosen AI providers

## Getting Help

If you encounter issues:
1. Run the test script: `python test_bsm.py`
2. Check the console output for errors
3. Verify all dependencies are installed
4. Make sure you have the required permissions