# BSM Developer Onboarding Guide

Welcome to the BSM (BullShit Meter) development team! This guide will help you get up and running with the codebase quickly.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [Development Workflow](#development-workflow)
5. [Code Style Guide](#code-style-guide)
6. [Testing Guidelines](#testing-guidelines)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Tesseract OCR
- OS-specific development tools

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd bsm

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the application
python -m bsm.main
```

## Development Environment Setup

### IDE Configuration

#### VS Code (Recommended)
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true
}
```

#### PyCharm
1. Open project root
2. Configure Python interpreter to use venv
3. Enable PyQt6 code completion
4. Set up run configuration for `bsm/main.py`

### Required Tools

#### Tesseract OCR Installation
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download installer from GitHub releases
```

#### Platform-Specific Dependencies

**macOS**:
- Xcode Command Line Tools
- Accessibility permissions for hotkeys

**Windows**:
- Visual Studio Build Tools
- Windows SDK

**Linux**:
- python3-dev
- libx11-dev (for hotkeys)

## Architecture Overview

### Directory Structure
```
bsm/
├── core/           # Business logic
│   ├── ai_providers.py    # AI integrations
│   ├── database.py        # Data persistence
│   └── settings.py        # Configuration
├── ui/             # User interface
│   ├── result_window.py   # Analysis display
│   ├── settings_window.py # Settings UI
│   └── context_window.py  # Context input
├── utils/          # Platform utilities
│   ├── hotkey_manager.py  # Global hotkeys
│   └── text_capture.py    # Text extraction
└── main.py         # Application entry
```

### Key Concepts

1. **Provider Pattern**: AI services are abstracted behind a common interface
2. **Worker Threads**: Long operations run in background threads
3. **Signal/Slot**: PyQt6 event system for UI updates
4. **Settings Manager**: Centralized configuration with encryption

### Data Flow
```
User Input → Text Capture → Analysis Worker → AI Provider
                                ↓
                        Database Storage
                                ↓
                        Result Window ← Markdown Rendering
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Run tests (when available)
pytest

# Commit with descriptive message
git commit -m "feat: add amazing new feature"

# Push to remote
git push origin feature/your-feature-name
```

### 2. Code Organization

**Adding a New AI Provider**:
1. Create class inheriting from `AIProvider`
2. Implement `analyze_text()` and `get_name()`
3. Register in `BSMApplication.setup_ai_providers()`

**Adding a New UI Window**:
1. Create new file in `bsm/ui/`
2. Inherit from `QMainWindow` or `QDialog`
3. Follow existing patterns for styling
4. Connect to main app via signals

### 3. Commit Message Convention
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: update dependencies
```

## Code Style Guide

### Python Style
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use f-strings for formatting

### Naming Conventions
```python
# Classes: PascalCase
class AnalysisWorker:
    pass

# Functions/Methods: snake_case
def analyze_text(text: str) -> dict:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30

# Private methods: leading underscore
def _internal_method(self):
    pass
```

### PyQt6 Conventions
```python
# Signals at class level
class MyWidget(QWidget):
    data_ready = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # UI setup code
        pass
```

### Documentation
```python
def analyze_text(self, text: str, mode: str = "balanced") -> Dict[str, Any]:
    """
    Analyze text using AI provider.
    
    Args:
        text: Text to analyze
        mode: Analysis mode (argumentative, balanced, helpful)
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ProviderError: If analysis fails
    """
    pass
```

## Testing Guidelines

### Test Structure
```
tests/
├── unit/
│   ├── test_ai_providers.py
│   ├── test_database.py
│   └── test_settings.py
├── integration/
│   └── test_analysis_flow.py
└── fixtures/
    └── sample_data.py
```

### Writing Tests
```python
import pytest
from bsm.core.settings import SettingsManager

class TestSettingsManager:
    @pytest.fixture
    def settings_manager(self, tmp_path):
        return SettingsManager(config_dir=str(tmp_path))
    
    def test_save_and_load(self, settings_manager):
        settings_manager.set('test_key', 'test_value')
        settings_manager.save_settings()
        
        # Reload
        new_manager = SettingsManager(settings_manager.config_dir)
        assert new_manager.get('test_key') == 'test_value'
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bsm

# Run specific test file
pytest tests/unit/test_settings.py

# Run with verbose output
pytest -v
```

## Common Tasks

### Adding a New Setting
1. Add to `DEFAULT_SETTINGS` in `settings.py`
2. Update settings UI in `settings_window.py`
3. Add migration logic if needed
4. Document in user guide

### Debugging UI Issues
```python
# Enable Qt debug output
import os
os.environ['QT_DEBUG_PLUGINS'] = '1'

# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use Qt Inspector
from PyQt6.QtWidgets import QApplication
app = QApplication.instance()
app.setStyleSheet("QWidget { border: 1px solid red; }")
```

### Performance Profiling
```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

# Print results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

#### Hotkey Not Working
1. Check OS permissions
2. Verify no conflicts
3. Try alternative combinations
4. Check logs for errors

#### UI Not Displaying
1. Verify PyQt6 installation
2. Check display server (Linux)
3. Update graphics drivers
4. Try `QT_QPA_PLATFORM=offscreen`

#### OCR Failures
1. Verify Tesseract installation
2. Check image quality
3. Ensure language packs installed
4. Review preprocessing options

### Debug Mode
```python
# Add to main.py for debug mode
if __name__ == "__main__":
    import sys
    if "--debug" in sys.argv:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        os.environ['PYTHONFAULTHANDLER'] = '1'
```

### Getting Help
1. Check existing issues on GitHub
2. Review documentation
3. Ask in development chat
4. Create detailed bug report

## Resources

### Documentation
- [BSM_Architecture.md](./BSM_Architecture.md) - System architecture
- [Module READMEs](./bsm/) - Component documentation
- [TASK_LIST.md](./TASK_LIST.md) - Development roadmap

### External Resources
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### Development Tools
- [Black](https://black.readthedocs.io/) - Code formatter
- [Pylint](https://pylint.org/) - Code linter
- [pytest](https://pytest.org/) - Testing framework

Welcome to the team! Happy coding! 🚀
