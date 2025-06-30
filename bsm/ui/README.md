# BSM UI Module

The UI module contains all PyQt6-based user interface components for the BSM application.

## Components

### result_window.py
**Purpose**: Displays analysis results in a beautiful, markdown-rendered window

**Key Classes**:
- `MarkdownRenderer`: Custom QWebEngineView for rendering markdown with syntax highlighting
- `ResultWindow`: Main window for displaying analysis results

**Features**:
- Dark theme with custom CSS styling
- Markdown rendering with code syntax highlighting
- Copy-to-clipboard functionality
- Window position persistence
- Resizable and movable

**CSS Customization**:
- Custom dark theme optimized for readability
- Syntax highlighting for code blocks
- Responsive design elements
- Professional typography

### settings_window.py
**Purpose**: Provides comprehensive settings management interface

**Key Classes**:
- `SettingsWindow`: Tabbed interface for all application settings
- `APIKeysTab`: Secure API key input and management
- `ProvidersTab`: LLM provider selection and configuration
- `HotkeyTab`: Global hotkey customization
- `AppearanceTab`: Theme and display preferences

**Features**:
- Tabbed organization for logical grouping
- Password-style input for API keys
- Real-time validation
- Apply/Cancel/OK button pattern
- Tooltips and help text

### context_window.py
**Purpose**: Allows users to provide additional context for analysis

**Key Classes**:
- `ContextWindow`: Modal dialog for context input
- `ContextEditor`: Enhanced text editor with formatting

**Features**:
- Optional workflow step
- Markdown preview
- Template suggestions
- Quick actions for common contexts
- History of recent contexts

### screenshot_selector.py
**Purpose**: Interactive screenshot region selection

**Key Classes**:
- `ScreenshotSelector`: Overlay widget for region selection
- `SelectionRect`: Visual feedback for selected area

**Features**:
- Full-screen overlay
- Rubber-band selection
- Crosshair cursor
- Dimension display
- Escape to cancel

## Design Patterns

1. **Model-View Pattern**: Separation of data and presentation
2. **Observer Pattern**: Qt signals/slots for event handling
3. **Template Method**: Base window behaviors
4. **Composite Pattern**: Nested UI components

## PyQt6 Best Practices

### Signal/Slot Connections
```python
# Use new-style connections
self.button.clicked.connect(self.on_button_clicked)

# Disconnect when needed
self.button.clicked.disconnect()
```

### Thread Safety
```python
# Always update UI from main thread
self.signal.emit(data)  # From worker thread
self.update_ui(data)    # In main thread slot
```

### Resource Management
```python
# Proper cleanup in closeEvent
def closeEvent(self, event):
    self.save_settings()
    self.cleanup_resources()
    super().closeEvent(event)
```

## Styling Guide

### Color Palette
- Background: `#2b2b2b` (dark gray)
- Text: `#ffffff` (white)
- Accent: `#4CAF50` (green) - to be replaced with crimson
- Secondary: `#555555` (medium gray)
- Error: `#f44336` (red)
- Warning: `#ff9800` (orange)

### Typography
- Headers: System font, bold
- Body: System font, regular
- Code: Monospace font family
- Base size: 14px

### Spacing
- Component margin: 16px
- Element padding: 8px
- Section spacing: 24px

## Accessibility Considerations

1. **Keyboard Navigation**: Tab order and shortcuts
2. **Screen Readers**: Proper labels and descriptions
3. **High Contrast**: Sufficient color contrast ratios
4. **Font Scaling**: Responsive to system font size

## Performance Optimizations

1. **Lazy Loading**: Load UI components on demand
2. **Virtual Scrolling**: For large result sets
3. **Debouncing**: For real-time updates
4. **Caching**: For rendered markdown

## Known Issues

1. **High DPI**: Some icons may appear blurry
2. **Focus**: Tab order needs refinement
3. **Animations**: Currently no smooth transitions
4. **Responsiveness**: Fixed minimum window sizes

## Future Enhancements

1. **Theming System**: User-customizable themes
2. **Animations**: Smooth transitions and effects
3. **Docking**: Draggable, dockable panels
4. **Touch Support**: Gesture recognition
5. **Accessibility**: Full WCAG 2.1 compliance
