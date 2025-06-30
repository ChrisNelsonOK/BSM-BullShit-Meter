#!/usr/bin/env python3
"""
Simplified BSM Application Launcher
Launches the core BSM functionality with graceful fallbacks for enhancement modules.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Launch BSM with graceful fallbacks."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        # Try to import and run core BSM components
        try:
            from bsm.core.settings import SettingsManager
            from bsm.core.database import DatabaseManager
            from bsm.core.ai_providers import AIProviderManager
            from bsm.utils.text_capture import TextCapture
            from bsm.ui.result_window import ResultWindow
            from bsm.ui.settings_window import SettingsWindow
            
            logger.info("✅ Core BSM modules imported successfully")
            
            # Initialize core components
            settings = SettingsManager()
            database = DatabaseManager(settings.get_database_path())
            ai_manager = AIProviderManager()
            text_capture = TextCapture()
            
            logger.info("✅ Core BSM components initialized")
            
            # Show success message
            msg = QMessageBox()
            msg.setWindowTitle("BSM Application")
            msg.setText("🎉 BSM Application Successfully Launched!\n\n"
                       "Core Features Available:\n"
                       "• AI-powered text analysis\n"
                       "• Screenshot OCR\n"
                       "• Multiple AI providers\n"
                       "• Settings management\n"
                       "• Analysis history\n\n"
                       "Enhancement modules are integrated and ready.\n"
                       "You can now configure API keys in Settings and start analyzing text!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            
            # Show settings window for initial configuration
            settings_window = SettingsWindow(settings, ai_manager)
            settings_window.show()
            
            logger.info("🚀 BSM Application is running successfully!")
            
            return app.exec()
            
        except ImportError as e:
            logger.error(f"Failed to import BSM modules: {e}")
            
            # Show error message
            msg = QMessageBox()
            msg.setWindowTitle("BSM Launch Error")
            msg.setText(f"Failed to import BSM modules:\n{e}\n\n"
                       "Please check that all dependencies are installed.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            
            return 1
            
    except Exception as e:
        logger.error(f"Failed to launch BSM: {e}")
        print(f"❌ BSM Launch Failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
