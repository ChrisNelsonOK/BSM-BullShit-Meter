#!/usr/bin/env python3
"""
BSM (BullShit Meter) - Clean Minimal Launch Version
A working, minimal version of the BSM application that will actually launch.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# BSM core imports (with error handling)
try:
    from bsm.core.settings import SettingsManager
    logger.info("✅ Settings manager imported")
except ImportError as e:
    logger.warning(f"Settings manager import failed: {e}")
    SettingsManager = None


class BSMMainWindow(QMainWindow):
    """Main BSM application window."""
    
    def __init__(self):
        super().__init__()
        self.settings_manager = None
        self.init_settings()
        self.init_ui()
        
    def init_settings(self):
        """Initialize settings manager."""
        if SettingsManager:
            try:
                self.settings_manager = SettingsManager()
                logger.info("✅ Settings manager initialized")
            except Exception as e:
                logger.error(f"Settings manager failed: {e}")
                
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BSM - BullShit Meter")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎯 BSM - BullShit Meter")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # Status
        status_text = "✅ BSM Application is running successfully!\n\n"
        if self.settings_manager:
            status_text += "🔧 Settings manager: Active\n"
        else:
            status_text += "⚠️ Settings manager: Not available\n"
            
        status_text += "\n📋 Available Features:\n"
        status_text += "• Basic application framework\n"
        status_text += "• Settings management (if available)\n"
        status_text += "• Ready for configuration\n\n"
        status_text += "🚀 Next Steps:\n"
        status_text += "• Configure API keys for AI analysis\n"
        status_text += "• Set up hotkeys for quick access\n"
        status_text += "• Enable advanced features"
        
        status = QLabel(status_text)
        status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status.setFont(QFont("Arial", 12))
        status.setStyleSheet("color: #34495e; background-color: #ecf0f1; padding: 20px; border-radius: 10px;")
        status.setWordWrap(True)
        
        # Text area for testing
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Paste text here to test BSM analysis (feature coming soon)...")
        self.text_area.setFont(QFont("Arial", 11))
        self.text_area.setStyleSheet("border: 2px solid #bdc3c7; border-radius: 5px; padding: 10px;")
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Analyze button (placeholder)
        analyze_btn = QPushButton("🔍 Analyze Text")
        analyze_btn.setFont(QFont("Arial", 12))
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_text)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setFont(QFont("Arial", 12))
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setFont(QFont("Arial", 12))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(analyze_btn)
        button_layout.addWidget(settings_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        # Add all widgets to layout
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addWidget(QLabel("📝 Test Area:"))
        layout.addWidget(self.text_area)
        layout.addLayout(button_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
    def analyze_text(self):
        """Placeholder for text analysis."""
        text = self.text_area.toPlainText().strip()
        if not text:
            self.text_area.setPlainText("Please enter some text to analyze!")
            return
            
        # Placeholder response
        result = f"\n\n🔍 BSM Analysis Results:\n"
        result += f"📊 Text length: {len(text)} characters\n"
        result += f"📝 Word count: {len(text.split())} words\n"
        result += f"⚠️ Note: Full AI analysis requires API key configuration\n"
        result += f"🚀 This is a placeholder - real analysis coming soon!"
        
        self.text_area.setPlainText(text + result)
        
    def show_settings(self):
        """Show settings dialog."""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("BSM Settings")
        msg.setText("⚙️ Settings Configuration\n\n"
                   "Settings features:\n"
                   "• API key management\n"
                   "• Hotkey configuration\n"
                   "• Theme selection\n"
                   "• Advanced options\n\n"
                   "Full settings dialog coming soon!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


class BSMApplication(QApplication):
    """Main BSM application class."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        self.setApplicationName("BSM")
        self.setApplicationDisplayName("BullShit Meter")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("BSM Development")
        
        # Create and show main window
        self.main_window = BSMMainWindow()
        self.main_window.show()
        
        logger.info("🎉 BSM Application launched successfully!")


def main():
    """Main entry point."""
    logger.info("🚀 Starting BSM Application...")
    
    # Create application
    app = BSMApplication(sys.argv)
    
    # Run application
    try:
        exit_code = app.exec()
        logger.info(f"BSM Application exited with code: {exit_code}")
        return exit_code
    except KeyboardInterrupt:
        logger.info("BSM Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"BSM Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
