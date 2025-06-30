# BSM (BullShit Meter)

An AI-powered cross-platform application that provides fact-checking and counter-argument analysis for selected text or screenshots. BSM runs in your system tray/menu bar and can be triggered with a global hotkey to analyze any text on your screen.

## Features

- **Global Hotkey**: Trigger analysis with a customizable hotkey (default: Ctrl+Shift+B)
- **Text Selection**: Analyzes currently selected text from any application
- **Screenshot OCR**: Extracts and analyzes text from screenshots using OCR
- **Multiple AI Providers**: Supports OpenAI, Claude, and local Ollama models
- **Attitude Modes**: 
  - **Argumentative**: Aggressive fact-checking focused on finding flaws
  - **Balanced**: Objective analysis with neutral tone
  - **Helpful**: Educational and constructive feedback
- **Beautiful Dark Theme**: Modern dark UI with sleek styling and readable formatting
- **Markdown Results**: Displays results in a resizable popup with beautifully formatted Markdown
- **History Storage**: Saves all analyses to a local SQLite database with search capabilities
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Privacy-Focused**: Encrypted API key storage and local-only data

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (for screenshot text extraction)
   - macOS: `brew install tesseract`
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### Install BSM

```bash
# Clone the repository
git clone <repository-url>
cd bsm

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

1. **Run BSM**:
   ```bash
   python -m bsm.main
   ```
   Or if installed:
   ```bash
   bsm
   ```

2. **Configure API Keys**:
   - Right-click the system tray icon
   - Select "Settings"
   - Add your OpenAI and/or Claude API keys
   - Configure your preferred LLM provider

3. **Use BSM**:
   - Select text anywhere on your screen
   - Press the global hotkey (Ctrl+Shift+B)
   - View the analysis results in the popup window

## Configuration

### API Keys

BSM supports multiple AI providers:

- **OpenAI**: Requires API key from OpenAI
- **Claude**: Requires API key from Anthropic
- **Ollama**: Local LLM (requires Ollama to be running)

### Attitude Modes

- **Argumentative**: Focuses on finding flaws and constructing strong counter-arguments
- **Balanced**: Provides objective, neutral analysis
- **Helpful**: Offers educational, constructive feedback

### Global Hotkey

Default hotkey is `Ctrl+Shift+B` (or `Cmd+Shift+B` on macOS). You can customize this in the settings.

## Usage Examples

### Analyzing Selected Text
1. Select text in any application (browser, document, etc.)
2. Press the global hotkey
3. BSM analyzes the text and shows results

### Analyzing Screenshots
1. If no text is selected, BSM can analyze screenshots
2. Press the global hotkey
3. BSM captures the screen, extracts text via OCR, and analyzes it

### System Tray Menu
- **Analyze Clipboard**: Analyzes text currently in clipboard
- **Analyze Screenshot**: Takes a screenshot and analyzes extracted text
- **Settings**: Opens the configuration window
- **Show History**: Views past analyses (coming soon)
- **Quit**: Exits the application

## File Structure

```
bsm/
├── bsm/
│   ├── core/
│   │   ├── settings.py          # Settings management with encryption
│   │   ├── database.py          # SQLite database operations
│   │   └── ai_providers.py      # AI provider implementations
│   ├── ui/
│   │   ├── result_window.py     # Main results display window
│   │   └── settings_window.py   # Settings configuration window
│   ├── utils/
│   │   ├── hotkey_manager.py    # Global hotkey management
│   │   └── text_capture.py      # Text selection and OCR
│   └── main.py                  # Main application entry point
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Running from Source

```bash
# Clone and enter directory
cd bsm

# Install in development mode
pip install -e .

# Run the application
python -m bsm.main
```

### Adding New AI Providers

1. Create a new provider class inheriting from `AIProvider` in `ai_providers.py`
2. Implement the required methods
3. Register the provider in the `BSMApplication.setup_ai_providers()` method

## Troubleshooting

### Hotkey Not Working
- Check if another application is using the same hotkey
- Try changing the hotkey in settings
- On macOS, ensure BSM has accessibility permissions

### OCR Not Working
- Verify Tesseract is installed and in PATH
- Check if tesseract path is correctly set for your platform
- Ensure screenshot permissions are granted

### API Errors
- Verify API keys are correct
- Check internet connection
- Ensure you have sufficient API credits

## Privacy & Security

- API keys are encrypted locally using Fernet encryption
- Analysis history is stored locally in SQLite database
- No data is sent to third parties except chosen AI providers
- All network requests are made directly to AI provider APIs

## License

[License information would go here]

## Contributing

[Contributing guidelines would go here]