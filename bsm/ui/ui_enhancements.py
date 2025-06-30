"""
UI/UX Enhancements for BSM Application.

This module provides modern UI components and accessibility features including:
- Theme management (dark/light mode)
- Toast notifications
- Flyout windows
- Keyboard navigation helpers
- High-DPI support
- Accessibility features
"""

import json
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsOpacityEffect, QApplication, QStyle,
    QDialog, QCheckBox, QComboBox, QSpinBox, QSlider,
    QGroupBox, QScrollArea, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve,
    pyqtSignal, QSize, QPoint, pyqtProperty
)
from PyQt6.QtGui import (
    QPalette, QColor, QFont, QPainter, QBrush, QPen,
    QPixmap, QIcon, QKeySequence, QShortcut
)

logger = logging.getLogger(__name__)


class Theme(Enum):
    """Available application themes."""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"  # Follow system theme


@dataclass
class ThemeColors:
    """Color scheme for a theme."""
    background: str
    surface: str
    primary: str
    secondary: str
    text: str
    text_secondary: str
    error: str
    warning: str
    success: str
    border: str


class ThemeManager:
    """Manages application themes and color schemes."""
    
    THEMES = {
        Theme.DARK: ThemeColors(
            background="#1e1e1e",
            surface="#2b2b2b",
            primary="#4CAF50",
            secondary="#FFC107",
            text="#ffffff",
            text_secondary="#cccccc",
            error="#f44336",
            warning="#ff9800",
            success="#4CAF50",
            border="#555555"
        ),
        Theme.LIGHT: ThemeColors(
            background="#ffffff",
            surface="#f5f5f5",
            primary="#2196F3",
            secondary="#FF5722",
            text="#000000",
            text_secondary="#666666",
            error="#d32f2f",
            warning="#f57c00",
            success="#388E3C",
            border="#cccccc"
        )
    }
    
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.current_theme = Theme.DARK
        self.custom_colors: Dict[str, str] = {}
        
        # Load theme preference
        if settings_manager:
            theme_name = settings_manager.get('theme', 'dark')
            self.current_theme = Theme(theme_name)
            self.custom_colors = settings_manager.get('custom_colors', {})
    
    def get_colors(self, theme: Optional[Theme] = None) -> ThemeColors:
        """Get color scheme for a theme."""
        if theme is None:
            theme = self.current_theme
        
        if theme == Theme.AUTO:
            # Detect system theme
            palette = QApplication.palette()
            is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
            theme = Theme.DARK if is_dark else Theme.LIGHT
        
        colors = self.THEMES[theme]
        
        # Apply custom colors
        if self.custom_colors:
            colors_dict = colors.__dict__.copy()
            colors_dict.update(self.custom_colors)
            return ThemeColors(**colors_dict)
        
        return colors
    
    def apply_theme(self, widget: QWidget, theme: Optional[Theme] = None):
        """Apply theme to a widget."""
        colors = self.get_colors(theme)
        
        # Generate stylesheet
        stylesheet = f"""
        QWidget {{
            background-color: {colors.background};
            color: {colors.text};
        }}
        
        QFrame {{
            background-color: {colors.surface};
            border: 1px solid {colors.border};
            border-radius: 8px;
        }}
        
        QPushButton {{
            background-color: {colors.primary};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {self._darken_color(colors.primary, 0.1)};
        }}
        
        QPushButton:pressed {{
            background-color: {self._darken_color(colors.primary, 0.2)};
        }}
        
        QLabel {{
            color: {colors.text};
        }}
        
        QComboBox, QSpinBox {{
            background-color: {colors.surface};
            border: 1px solid {colors.border};
            padding: 4px;
            border-radius: 4px;
        }}
        
        QCheckBox, QRadioButton {{
            color: {colors.text};
        }}
        
        QScrollBar:vertical {{
            background-color: {colors.surface};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.border};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.primary};
        }}
        """
        
        widget.setStyleSheet(stylesheet)
    
    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a color by a factor."""
        qcolor = QColor(color)
        h, s, l, a = qcolor.getHslF()
        qcolor.setHslF(h, s, max(0, l - factor), a)
        return qcolor.name()
    
    def set_theme(self, theme: Theme):
        """Set the current theme."""
        self.current_theme = theme
        if self.settings_manager:
            self.settings_manager.set('theme', theme.value)
            self.settings_manager.save_settings()
    
    def set_custom_color(self, key: str, color: str):
        """Set a custom color override."""
        self.custom_colors[key] = color
        if self.settings_manager:
            self.settings_manager.set('custom_colors', self.custom_colors)
            self.settings_manager.save_settings()


class ToastNotification(QFrame):
    """Modern toast notification widget."""
    
    class Type(Enum):
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
    
    closed = pyqtSignal()
    
    def __init__(self, 
                 message: str,
                 toast_type: Type = Type.INFO,
                 duration: int = 3000,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup the toast UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        
        # Set icon based on type
        icon_map = {
            self.Type.INFO: "ℹ️",
            self.Type.SUCCESS: "✅",
            self.Type.WARNING: "⚠️",
            self.Type.ERROR: "❌"
        }
        icon_label.setText(icon_map[self.toast_type])
        icon_label.setStyleSheet("font-size: 18px;")
        
        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(300)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                color: #ffffff;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(close_btn)
        
        # Style based on type
        color_map = {
            self.Type.INFO: "#2196F3",
            self.Type.SUCCESS: "#4CAF50",
            self.Type.WARNING: "#FF9800",
            self.Type.ERROR: "#F44336"
        }
        
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {color_map[self.toast_type]};
                border-radius: 8px;
            }}
            QLabel {{
                color: white;
                font-size: 14px;
            }}
        """)
        
        # Shadow effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        """Setup fade in/out animations."""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Fade out animation
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out.finished.connect(self._on_fade_out_finished)
        
        # Auto-close timer
        if self.duration > 0:
            self.close_timer = QTimer()
            self.close_timer.timeout.connect(self.close)
            self.close_timer.setSingleShot(True)
    
    def show_toast(self, parent_widget: Optional[QWidget] = None):
        """Show the toast notification."""
        # Position the toast
        if parent_widget:
            parent_rect = parent_widget.geometry()
            x = parent_rect.x() + parent_rect.width() - self.width() - 20
            y = parent_rect.y() + 20
            self.move(x, y)
        else:
            # Center on screen
            screen = QApplication.primaryScreen()
            if screen:
                screen_rect = screen.availableGeometry()
                x = screen_rect.width() - self.width() - 20
                y = 20
                self.move(x, y)
        
        self.show()
        self.fade_in.start()
        
        if self.duration > 0:
            self.close_timer.start(self.duration)
    
    def close(self):
        """Close with fade out animation."""
        self.fade_out.start()
    
    def _on_fade_out_finished(self):
        """Handle fade out completion."""
        self.closed.emit()
        super().close()


class FlyoutWindow(QDialog):
    """Modern flyout/popup window."""
    
    def __init__(self, 
                 title: str,
                 parent: Optional[QWidget] = None,
                 width: int = 400,
                 height: int = 300):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(width, height)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the flyout UI."""
        # Main container
        self.container = QFrame(self)
        self.container.setObjectName("flyoutContainer")
        
        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.windowTitle())
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        container_layout.addLayout(header_layout)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        container_layout.addWidget(self.content_widget, 1)
        
        # Style
        self.container.setStyleSheet("""
            #flyoutContainer {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 12px;
            }
        """)
        
        # Shadow
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.container.setGraphicsEffect(shadow)
    
    def set_content(self, widget: QWidget):
        """Set the content widget."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.content_layout.addWidget(widget)
    
    def show_at(self, pos: QPoint):
        """Show the flyout at a specific position."""
        self.move(pos)
        self.show()


class AccessibilityManager:
    """Manages accessibility features."""
    
    def __init__(self):
        self.high_contrast = False
        self.large_text = False
        self.keyboard_nav_indicators = True
        self.screen_reader_mode = False
    
    def apply_accessibility_features(self, widget: QWidget):
        """Apply accessibility features to a widget."""
        if self.high_contrast:
            self._apply_high_contrast(widget)
        
        if self.large_text:
            self._apply_large_text(widget)
        
        if self.keyboard_nav_indicators:
            self._setup_keyboard_navigation(widget)
    
    def _apply_high_contrast(self, widget: QWidget):
        """Apply high contrast mode."""
        widget.setStyleSheet(widget.styleSheet() + """
            QWidget { outline: 2px solid yellow; }
            QPushButton:focus { border: 3px solid #00ff00; }
            QLineEdit:focus { border: 3px solid #00ff00; }
        """)
    
    def _apply_large_text(self, widget: QWidget):
        """Apply large text mode."""
        font = widget.font()
        font.setPointSize(int(font.pointSize() * 1.5))
        widget.setFont(font)
    
    def _setup_keyboard_navigation(self, widget: QWidget):
        """Setup enhanced keyboard navigation."""
        # Add tab order hints
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Add keyboard shortcuts for common actions
        if hasattr(widget, 'close'):
            QShortcut(QKeySequence("Escape"), widget, widget.close)


class UIEnhancementSettings(QDialog):
    """Settings dialog for UI enhancements."""
    
    def __init__(self, theme_manager: ThemeManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("UI Enhancement Settings")
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the settings UI."""
        layout = QVBoxLayout(self)
        
        # Theme settings
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selection
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([t.value.title() for t in Theme])
        self.theme_combo.setCurrentText(self.theme_manager.current_theme.value.title())
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        # Custom colors
        colors_label = QLabel("Custom Colors:")
        theme_layout.addWidget(colors_label)
        
        # Color customization would go here
        
        layout.addWidget(theme_group)
        
        # Accessibility settings
        access_group = QGroupBox("Accessibility")
        access_layout = QVBoxLayout(access_group)
        
        self.high_contrast_check = QCheckBox("High Contrast Mode")
        self.large_text_check = QCheckBox("Large Text")
        self.keyboard_nav_check = QCheckBox("Enhanced Keyboard Navigation")
        self.screen_reader_check = QCheckBox("Screen Reader Optimizations")
        
        access_layout.addWidget(self.high_contrast_check)
        access_layout.addWidget(self.large_text_check)
        access_layout.addWidget(self.keyboard_nav_check)
        access_layout.addWidget(self.screen_reader_check)
        
        layout.addWidget(access_group)
        
        # Notification settings
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout(notif_group)
        
        self.toast_duration_label = QLabel("Toast Duration (ms):")
        self.toast_duration_spin = QSpinBox()
        self.toast_duration_spin.setRange(1000, 10000)
        self.toast_duration_spin.setSingleStep(500)
        self.toast_duration_spin.setValue(3000)
        
        notif_layout.addWidget(self.toast_duration_label)
        notif_layout.addWidget(self.toast_duration_spin)
        
        layout.addWidget(notif_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()


def create_toast(message: str, 
                toast_type: ToastNotification.Type = ToastNotification.Type.INFO,
                duration: int = 3000,
                parent: Optional[QWidget] = None) -> ToastNotification:
    """Convenience function to create and show a toast notification."""
    toast = ToastNotification(message, toast_type, duration, parent)
    toast.show_toast(parent)
    return toast
