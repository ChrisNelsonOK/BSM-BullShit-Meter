# BSM Utils Module

The utils module provides cross-platform utility functions and system integration components.

## Components

### hotkey_manager.py
**Purpose**: Cross-platform global hotkey registration and management

**Key Functions**:
- `create_hotkey_manager()`: Factory function that returns platform-appropriate manager
- `parse_hotkey()`: Converts string representation to key codes
- `register_hotkey()`: Registers global hotkey with callback
- `unregister_hotkey()`: Removes hotkey registration

**Platform Support**:
- Windows: Uses `keyboard` library
- macOS: Falls back to `pynput` or native implementation
- Linux: Uses `pynput` with X11

**Hotkey Format**:
```
Modifiers: ctrl, shift, alt, cmd/win/super
Keys: a-z, 0-9, f1-f12, special keys
Format: "ctrl+shift+b" or "cmd+alt+f1"
```

**Error Handling**:
- Graceful fallback between backends
- Permission error handling for macOS
- Clear error messages for invalid hotkeys

### macos_hotkey_manager.py
**Purpose**: macOS-specific hotkey implementation using native APIs

**Key Features**:
- AppKit integration for better reliability
- Accessibility permissions handling
- Native key code mapping
- System-level hotkey registration

**Requirements**:
- macOS 10.12+
- Accessibility permissions
- PyObjC framework

### text_capture.py
**Purpose**: Extract text from various sources (clipboard, selection, screenshots)

**Key Classes**:
- `TextCapture`: Main interface for text extraction
- `ScreenshotCapture`: Screenshot-based text extraction
- `SelectionCapture`: Active selection capture

**Features**:
- Cross-platform clipboard access
- Selection capture with fallbacks
- OCR integration via Tesseract
- Platform-specific optimizations

**OCR Pipeline**:
```python
Screenshot → Image Preprocessing → Tesseract OCR → Text Cleanup → Result
```

**Tesseract Configuration**:
- Auto-detection of installation
- Custom path support
- Language pack management
- Performance optimization settings

## Platform-Specific Implementations

### Windows
- Clipboard: `win32clipboard`
- Selection: `pyautogui` simulation
- Hotkeys: `keyboard` library
- OCR: Direct Tesseract integration

### macOS
- Clipboard: `pbcopy/pbpaste` or AppKit
- Selection: Accessibility APIs
- Hotkeys: AppKit or `pynput`
- OCR: Tesseract with Homebrew paths

### Linux
- Clipboard: `xclip` or `pyperclip`
- Selection: X11 selection buffer
- Hotkeys: `pynput` with X11
- OCR: System Tesseract

## Best Practices

### Error Handling
```python
try:
    # Platform-specific operation
    result = platform_specific_function()
except PlatformError:
    # Try fallback
    result = fallback_function()
except PermissionError:
    # Guide user to fix permissions
    show_permission_guide()
```

### Platform Detection
```python
import platform
import sys

def get_platform():
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system in ['linux', 'freebsd']:
        return 'linux'
    else:
        return 'unknown'
```

### Resource Management
```python
# Always cleanup resources
def capture_screenshot():
    screenshot = None
    try:
        screenshot = take_screenshot()
        return process_image(screenshot)
    finally:
        if screenshot:
            screenshot.close()
```

## Dependencies

### Core
- `pyautogui`: Cross-platform GUI automation
- `pillow`: Image processing
- `pytesseract`: OCR wrapper
- `pyperclip`: Clipboard access

### Platform-Specific
- **Windows**: `pywin32`, `keyboard`
- **macOS**: `pyobjc`, `pynput`
- **Linux**: `python-xlib`, `pynput`

## Configuration

### Tesseract Setup
```python
# Auto-detection paths
TESSERACT_PATHS = {
    'windows': [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    ],
    'macos': [
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract'
    ],
    'linux': [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract'
    ]
}
```

### Hotkey Defaults
```python
DEFAULT_HOTKEYS = {
    'analyze': 'ctrl+shift+b',
    'screenshot': 'ctrl+shift+s',
    'settings': 'ctrl+shift+comma'
}
```

## Troubleshooting

### Common Issues

1. **Hotkey Not Working**
   - Check permissions (especially macOS)
   - Verify no conflicts with system hotkeys
   - Try alternative key combinations

2. **OCR Accuracy**
   - Ensure Tesseract is installed
   - Check image quality/resolution
   - Try preprocessing options

3. **Clipboard Access**
   - Verify clipboard permissions
   - Check for clipboard managers
   - Try alternative backends

## Performance Considerations

1. **OCR Optimization**
   - Limit capture area
   - Preprocess images
   - Cache results
   - Use appropriate PSM modes

2. **Hotkey Efficiency**
   - Minimal callback execution time
   - Async processing for heavy operations
   - Debounce rapid triggers

3. **Memory Management**
   - Release screenshots after processing
   - Clear clipboard after reading
   - Limit history storage

## Future Improvements

1. **Enhanced OCR**
   - Multiple OCR engine support
   - ML-based preprocessing
   - Layout analysis
   - Multi-language support

2. **Better Platform Integration**
   - Native clipboard monitoring
   - System notification integration
   - OS-specific optimizations

3. **Advanced Features**
   - Voice input support
   - Gesture recognition
   - Multi-monitor awareness
   - Cloud OCR services
