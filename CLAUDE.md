# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BSM (BullShit Meter) is a cross-platform Python application that provides AI-powered fact-checking and counter-argument analysis. It runs in the system tray with global hotkey support for analyzing selected text or screenshots.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Install Tesseract OCR (required for screenshot analysis)
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
```

### Running the Application
```bash
# Run from source
python -m bsm.main

# Or use the run script
python run.py

# Or if installed
bsm
```

### Testing
No formal test suite is currently implemented. Test manually by:
1. Running the application
2. Testing hotkey functionality
3. Testing text selection and screenshot capture
4. Verifying AI provider integrations

## Architecture Overview

### Core Components
- **`bsm/main.py`** - Main application with PyQt6 GUI and system tray
- **`bsm/core/settings.py`** - Encrypted settings management
- **`bsm/core/database.py`** - SQLite database for analysis history
- **`bsm/core/ai_providers.py`** - AI provider abstractions (OpenAI, Claude, Ollama)

### User Interface
- **`bsm/ui/result_window.py`** - Markdown results display window
- **`bsm/ui/settings_window.py`** - Settings configuration dialog

### Utilities
- **`bsm/utils/hotkey_manager.py`** - Cross-platform global hotkey management
- **`bsm/utils/text_capture.py`** - Text selection and screenshot OCR

### Key Design Patterns
- **Provider Pattern**: AI providers implement common interface for different APIs
- **Settings Manager**: Centralized configuration with encryption for sensitive data
- **Worker Threads**: AI analysis runs in separate threads to prevent UI blocking
- **Signal/Slot**: PyQt6 signals for communication between components

## Important Implementation Details

### Security
- API keys are encrypted using Fernet encryption before storage
- Database stores analysis history locally only
- No telemetry or data collection

### Cross-Platform Considerations
- Uses `pynput` for global hotkeys with platform-specific handling
- Tesseract OCR paths are configured per platform
- PyQt6 provides cross-platform GUI framework

### AI Provider Integration
- Async/await pattern for API calls
- Fallback provider system (primary → secondary → local)
- Structured JSON response format expected from providers

### Dependencies
- **PyQt6**: GUI framework and system tray
- **pynput**: Global hotkey capture
- **pytesseract**: OCR for screenshot analysis
- **openai/anthropic**: API clients for AI providers
- **pystray**: System tray icon (fallback)
- **cryptography**: Settings encryption

## Configuration Files

- **`~/.bsm/settings.yaml`** - User settings (API keys encrypted)
- **`~/.bsm/.key`** - Encryption key for sensitive data
- **`~/.bsm/bsm_history.db`** - SQLite database for analysis history

## Troubleshooting Common Issues

- **Hotkey not working**: Check accessibility permissions on macOS
- **OCR failing**: Verify tesseract installation and PATH
- **API errors**: Check API keys and network connectivity
- **Import errors**: Ensure all dependencies are installed