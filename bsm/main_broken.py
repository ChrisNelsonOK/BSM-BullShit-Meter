#!/usr/bin/env python3
"""
BSM (BullShit Meter) - Main Application
AI-powered fact checker and counter-argument generator
"""

import sys
import os
import asyncio
import logging
import signal
from typing import Optional
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QCoreApplication, Qt
from PyQt6.QtGui import QIcon, QPixmap, QClipboard
import pystray
from PIL import Image
import threading

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
    def cleanup(self):
        """Clean up resources on application exit."""
        logger.info("Cleaning up BSM application...")
        if hasattr(self, 'main_window'):
            self.main_window.close()


def main():
        """Create a default icon for the system tray."""
        # Create a simple icon programmatically
        try:
            pixmap = QPixmap(32, 32)
            pixmap.fill()  # Fill with default color
            return QIcon(pixmap)
        except Exception as e:
            print(f"Error creating icon: {e}")
            # Return empty icon as fallback
            return QIcon()
    
    def setup_hotkey(self):
        """Setup global hotkeys including attitude mode switching."""
        # Main analysis hotkey
        hotkey = self.settings_manager.get('global_hotkey', 'ctrl+shift+b')
        success, error = self.hotkey_manager.register_hotkey(
            'main_analysis',
            hotkey,
            self.hotkey_triggered,
            "Trigger BSM analysis"
        )
        if not success:
            logger.error(f"Failed to register main hotkey {hotkey}: {error}")
            self.show_notification("Hotkey Error", f"Failed to register hotkey: {error}")
        
        # Attitude mode hotkeys
        attitude_hotkeys = {
            'argumentative': self.settings_manager.get('hotkey_argumentative', 'ctrl+shift+1'),
            'balanced': self.settings_manager.get('hotkey_balanced', 'ctrl+shift+2'),
            'helpful': self.settings_manager.get('hotkey_helpful', 'ctrl+shift+3')
        }
        
        for mode, hotkey_combo in attitude_hotkeys.items():
            if hotkey_combo:  # Only register if configured
                success, error = self.hotkey_manager.register_hotkey(
                    f'attitude_{mode}',
                    hotkey_combo,
                    lambda m=mode: self.switch_attitude_mode(m),
                    f"Switch to {mode} attitude mode"
                )
                if not success:
                    logger.warning(f"Failed to register {mode} hotkey: {error}")
        
        # Start the hotkey manager
        self.hotkey_manager.start()
    
    def setup_tesseract(self):
        """Setup Tesseract OCR."""
        setup_tesseract()
    
    def setup_plugins(self):
        """Setup and load plugins."""
        try:
            # Plugin manager already loads plugins during initialization
            # Just register enabled plugins with AI manager
            enabled_plugins = self.plugin_manager.get_enabled_plugins()
            
            for plugin_info in enabled_plugins:
                try:
                    # Create provider instance from plugin
                    provider = self.plugin_manager.create_provider_instance(
                        plugin_info.name,
                        config={}
                    )
                    if provider:
                        self.ai_manager.add_provider(plugin_info.name, provider)
                        logger.info(f"Registered plugin provider: {plugin_info.display_name}")
                except Exception as e:
                    logger.warning(f"Failed to register plugin {plugin_info.name}: {e}")
                        
            logger.info(f"Loaded {len(enabled_plugins)} plugins")
            
        except Exception as e:
            logger.error(f"Failed to setup plugins: {e}")
    
    def setup_theme(self):
        """Setup theme management."""
        try:
            # Load theme from settings
            from bsm.ui.ui_enhancements import Theme
            theme_name = self.settings_manager.get('theme', 'dark')
            
            # Convert string to Theme enum
            if theme_name == 'dark':
                theme = Theme.DARK
            elif theme_name == 'light':
                theme = Theme.LIGHT
            else:
                theme = Theme.DARK  # Default fallback
                
            self.theme_manager.set_theme(theme)
            
            # Apply theme to application
            self.theme_manager.apply_theme(self)
            
            logger.info(f"Applied theme: {theme_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup theme: {e}")
    
    def setup_accessibility(self):
        """Setup accessibility features."""
        try:
            # Enable accessibility features based on settings
            if self.settings_manager.get('accessibility_enabled', True):
                self.accessibility_manager.apply_accessibility_features(self)
                
            # Setup keyboard navigation
            if self.settings_manager.get('keyboard_navigation', True):
                self.accessibility_manager.setup_keyboard_navigation(self)
                
            logger.info("Accessibility features enabled")
            
        except Exception as e:
            logger.error(f"Failed to setup accessibility: {e}")
    
    def setup_async_database(self):
        """Setup async database and run migrations."""
        try:
            # Run in async context
            import asyncio
            
            async def init_db():
                await self.async_database.initialize()
                await self.async_database.run_migrations()
                
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            loop.run_until_complete(init_db())
            logger.info("Async database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup async database: {e}")
            # Fallback to sync database
            logger.info("Falling back to synchronous database")
    
    def switch_attitude_mode(self, mode: str):
        """Switch the attitude mode for AI analysis."""
        valid_modes = ['argumentative', 'balanced', 'helpful']
        if mode not in valid_modes:
            logger.warning(f"Invalid attitude mode: {mode}")
            return
        
        current_mode = self.settings_manager.get('attitude_mode', 'balanced')
        if mode == current_mode:
            self.show_notification("Attitude Mode", f"Already in {mode} mode")
            return
        
        self.settings_manager.set('attitude_mode', mode)
        self.settings_manager.save_settings()
        
        # Update UI if result window is open
        if self.result_window:
            self.result_window.update_attitude_indicator(mode)
        
        # Show notification
        mode_descriptions = {
            'argumentative': 'Aggressive, debate-focused analysis',
            'balanced': 'Objective, neutral analysis',
            'helpful': 'Educational, constructive feedback'
        }
        self.show_notification(
            "Attitude Mode Changed", 
            f"Switched to {mode.title()} mode: {mode_descriptions.get(mode, '')}"
        )
        logger.info(f"Attitude mode switched to: {mode}")
    
    def hotkey_triggered(self):
        """Handle global hotkey activation."""
        try:
            # First try to get selected text
            selected_text = self.text_capture.get_selected_text()
            
            if selected_text and len(selected_text.strip()) > 0:
                self.analyze_text(selected_text, 'selection')
            else:
                # If no text selected, try screenshot OCR
                if self.settings_manager.get('enable_screenshot_ocr', True):
                    self.analyze_screenshot()
                else:
                    self.show_notification("No text selected", "Please select text to analyze or enable screenshot OCR in settings.")
        except Exception as e:
            self.show_notification("Error", f"Failed to capture text: {e}")
    
    def analyze_clipboard(self):
        """Analyze text from clipboard."""
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            
            if text and len(text.strip()) > 0:
                self.analyze_text(text, 'clipboard')
            else:
                self.show_notification("No text", "Clipboard is empty or contains no text.")
        except Exception as e:
            print(f"Clipboard error: {e}")
            self.show_notification("Clipboard Error", f"Failed to access clipboard: {e}")
    
    def analyze_screenshot(self):
        """Analyze text from screenshot."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # Simple confirmation dialog
            reply = QMessageBox.question(
                None,
                "Screenshot Analysis",
                "This will capture your entire screen and extract text.\nMake sure the text you want to analyze is visible.\n\nProceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Short delay to let user prepare
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self._do_screenshot_capture)
            self.show_notification("Screenshot in 2 seconds", "Get ready...")
            
        except Exception as e:
            print(f"Screenshot error: {e}")
            self.show_notification("Screenshot Error", f"Failed to setup screenshot: {e}")
    
    def _do_screenshot_capture(self):
        """Perform the actual screenshot capture using enhanced OCR."""
        try:
            # Use enhanced OCR for better text extraction
            async def capture_and_process():
                # Capture screenshot
                screenshot = self.text_capture.capture_screenshot()
                if not screenshot:
                    return None, "Failed to capture screenshot"
                
                # Process with enhanced OCR
                result = await self.enhanced_ocr.process_image_async(
                    screenshot,
                    preprocessing_mode='adaptive',
                    use_cache=True
                )
                
                return result.text if result else None, None
            
            # Submit async task
            task_id = self.task_manager.submit_task(
                capture_and_process(),
                priority=1,
                description="Enhanced screenshot OCR"
            )
            
            # Store task for completion handling
            self._active_analysis_tasks[task_id] = {
                'type': 'screenshot_ocr',
                'source': 'screenshot'
            }
            
            # Show progress notification
            create_toast(
                "Processing Screenshot: Extracting text with enhanced OCR...",
                ToastNotification.Type.INFO,
                duration=3000,
                parent=self
            )
                
        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            self.show_notification("Screenshot Error", f"Failed to capture screenshot: {e}")
    
    def analyze_text(self, text: str, source_type: str):
        """Analyze text using AI providers."""
        if not text or len(text.strip()) < 10:
            self.show_notification("Text too short", "Please provide more text for analysis (at least 10 characters).")
            return
        
        # Check if we have any AI providers configured
        if not self.ai_manager.providers:
            self.show_notification("No AI Providers", "Please configure API keys in Settings before analyzing text.")
            self.show_settings()
            return
        
        # Show context window for better analysis
        context_window = ContextWindow(text, source_type)
        
        # Store reference to prevent garbage collection
        self.context_window = context_window
        
        context_window.analysis_requested.connect(self.analyze_with_context)
        
        # Show as non-modal but prominent window
        context_window.show()
        context_window.raise_()
        context_window.activateWindow()
    
    def analyze_with_context(self, text: str, context_data: dict):
        """Analyze text with provided context."""
        attitude_mode = context_data.get('attitude_mode', 'balanced')
        
        # Check if analysis already exists
        try:
            existing_analysis = self.database_manager.get_analysis_by_hash(text, attitude_mode)
        except Exception as e:
            print(f"Database error: {e}")
            existing_analysis = None
        
        if existing_analysis:
            # Show existing analysis
            self.show_results(existing_analysis['analysis_result'], text)
            return
        
        # Show loading notification
        self.show_notification("Analyzing...", "BSM is analyzing the text with context. Please wait.")
        
        # Start analysis in worker thread
        self.start_analysis_worker(text, context_data.get('source_type', 'unknown'), attitude_mode, context_data)
    
    def start_analysis_worker(self, text: str, source_type: str, attitude_mode: str, context_data: dict = None):
        """Start analysis using AsyncTaskManager."""
        primary_provider = self.settings_manager.get('llm_provider', 'openai')
        
        # Generate unique task ID
        task_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        # Store analysis metadata for later use
        self._active_analysis_tasks[task_id] = {
            'text': text,
            'source_type': source_type,
            'attitude_mode': attitude_mode,
            'context_data': context_data
        }
        
        # Submit async task with timeout
        self.task_manager.submit_async_task(
            task_id,
            self.ai_manager.analyze_with_fallback,
            text,
            attitude_mode,
            primary_provider,
            ['ollama', 'openai', 'claude'],  # Fallback order
            timeout=60.0  # 60 second timeout
        )
    
    def _on_analysis_completed(self, task_id: str, result: dict):
        """Handle completed analysis from AsyncTaskManager."""
        # Get task metadata
        task_data = self._active_analysis_tasks.pop(task_id, None)
        if not task_data:
            return
        
        task_type = task_data.get('type', 'analysis')
        
        # Handle different task types
        if task_type == 'screenshot_ocr':
            self._handle_ocr_completion(task_id, result, task_data)
        elif task_type == 'analysis':
            self._handle_analysis_completion(task_id, result, task_data)
        else:
            logger.warning(f"Unknown task type: {task_type}")
    
    def _handle_ocr_completion(self, task_id: str, result, task_data: dict):
        """Handle OCR task completion."""
        text, error = result if isinstance(result, tuple) else (result, None)
        
        if error or not text:
            self.show_notification("OCR Failed", error or "No text could be extracted from the screenshot.")
            return
        
        if len(text.strip()) > 0:
            # Track OCR success
            self.telemetry.track_event('ocr_success', {
                'source': task_data.get('source', 'unknown'),
                'text_length': len(text)
            })
            
            # Proceed with analysis
            self.analyze_text(text, task_data.get('source', 'screenshot'))
        else:
            self.show_notification("No text found", "No text could be extracted from the screenshot.")
    
    def _handle_analysis_completion(self, task_id: str, result: dict, task_data: dict):
        """Handle AI analysis completion."""
        original_text = task_data['text']
        source_type = task_data['source_type']
        attitude_mode = task_data['attitude_mode']
        
        # Track analysis completion
        self.telemetry.track_event('analysis_completed', {
            'provider': result.get('provider_used', 'unknown'),
            'attitude_mode': attitude_mode,
            'source_type': source_type,
            'text_length': len(original_text)
        })
        
        # Save to async database if enabled
        if self.settings_manager.get('auto_save_results', True):
            try:
                # Use async database for better performance
                async def save_analysis():
                    await self.async_database.save_analysis(
                        text=original_text,
                        source_type=source_type,
                        analysis_result=result,
                        attitude_mode=attitude_mode,
                        provider_used=result.get('provider_used', 'unknown'),
                        confidence_score=result.get('confidence_score', 0.0)
                    )
                
                # Submit as background task
                self.task_manager.submit_task(
                    save_analysis(),
                    priority=3,  # Low priority
                    description="Save analysis to database"
                )
                
            except Exception as e:
                logger.error(f"Failed to save analysis: {e}")
                # Fallback to sync database
                try:
                    self.database_manager.save_analysis(
                        original_text,
                        source_type,
                        result,
                        attitude_mode,
                        result.get('provider_used', 'unknown'),
                        result.get('confidence_score', 0.0)
                    )
                except Exception as sync_error:
                    logger.error(f"Sync database fallback failed: {sync_error}")
        
        # Show results with enhanced UI
        self.show_results(result, original_text)
    
    def _on_analysis_failed(self, task_id: str, error_message: str):
        """Handle analysis error from AsyncTaskManager."""
        # Clean up task data
        self._active_analysis_tasks.pop(task_id, None)
        
        # Show error notification
        self.show_notification("Analysis Error", f"Failed to analyze text: {error_message}")
    
    def _on_analysis_progress(self, task_id: str, progress: int):
        """Handle analysis progress updates."""
        # Could update UI with progress indicator in the future
        logging.debug(f"Analysis {task_id} progress: {progress}%")
    
    def show_results(self, analysis_result: dict, original_text: str):
        """Show analysis results in popup window."""
        if not self.result_window:
            self.result_window = ResultWindow()
            self.result_window.closed.connect(self.result_window_closed)
            self.result_window.copy_requested.connect(self.copy_to_clipboard)
            
            # Restore window position
            position = self.settings_manager.get('window_position', {})
            if position:
                self.result_window.restore_position(position)
        
        self.result_window.display_analysis(analysis_result, original_text)
        self.result_window.show()
        self.result_window.raise_()
        self.result_window.activateWindow()
    
    def result_window_closed(self):
        """Handle result window close."""
        if self.result_window:
            # Save window position
            position = self.result_window.save_position()
            self.settings_manager.set('window_position', position)
            self.settings_manager.save_settings()
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    def show_settings(self):
        """Show settings window."""
        try:
            # Always create a new settings window to avoid reference issues
            if self.settings_window:
                self.settings_window.close()
                self.settings_window = None
            
            self.settings_window = SettingsWindow(self.settings_manager)
            self.settings_window.settings_changed.connect(self.settings_updated)
            
            # Handle window close
            self.settings_window.finished.connect(self.on_settings_window_closed)
            
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
        except Exception as e:
            print(f"Error showing settings window: {e}")
            import traceback
            traceback.print_exc()
            self.show_notification("Settings Error", f"Failed to open settings: {e}")
    
    def on_settings_window_closed(self):
        """Handle settings window being closed."""
        try:
            if self.settings_window:
                self.settings_window = None
        except Exception as e:
            print(f"Error handling settings window close: {e}")
    
    def settings_updated(self, new_settings: dict):
        """Handle settings update."""
        try:
            print("Settings updated, reloading configuration...")
            
            # Reload AI providers
            self.ai_manager = AIProviderManager()
            self.setup_ai_providers()
            
            # Update hotkey safely
            if self.hotkey_manager:
                self.hotkey_manager.stop()
            self.setup_hotkey()
            
            # Use QTimer to delay notification to ensure main thread
            QTimer.singleShot(100, lambda: self.show_notification("Settings Updated", "BSM settings have been updated successfully."))
            
        except Exception as e:
            print(f"Error updating settings: {e}")
            import traceback
            traceback.print_exc()
            # Use QTimer for error notification too
            QTimer.singleShot(100, lambda: self.show_notification("Settings Error", f"Error updating settings: {e}"))
    
    def show_history(self):
        """Show analysis history."""
        try:
            # Get recent analyses from database
            analyses = self.database_manager.get_recent_analyses(limit=10)
            
            if not analyses:
                self.show_notification("No History", "No previous analyses found.")
                return
            
            # Show a simple dialog with recent analyses
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox()
            msg.setWindowTitle("Analysis History")
            msg.setIcon(QMessageBox.Icon.Information)
            
            history_text = f"Found {len(analyses)} recent analyses:\n\n"
            for i, analysis in enumerate(analyses[:5], 1):
                original_text = analysis.get('original_text', '')
                
                # Clean up the text preview
                if original_text:
                    # Remove non-printable characters and clean up
                    clean_text = ''.join(char for char in original_text if char.isprintable() or char.isspace())
                    # Remove excessive whitespace
                    clean_text = ' '.join(clean_text.split())
                    text_preview = clean_text[:50] if clean_text else "No text"
                else:
                    text_preview = "No text"
                
                timestamp = analysis.get('created_at', 'Unknown')
                history_text += f"{i}. {text_preview}... ({timestamp})\n"
            
            if len(analyses) > 5:
                history_text += f"\n... and {len(analyses) - 5} more"
            
            msg.setText(history_text)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
        except Exception as e:
            print(f"History error: {e}")
            self.show_notification("History Error", f"Failed to load history: {e}")
    
    def tray_activated(self, reason):
        """Handle system tray activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()
    
    def show_notification(self, title: str, message: str):
        """Show system tray notification."""
        # Always emit signal to ensure main thread execution
        self.notification_requested.emit(title, message)
    
    def _show_notification_impl(self, title: str, message: str):
        """Internal implementation of show notification (main thread only)."""
        try:
            if self.system_tray:
                self.system_tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def quit_application(self):
        """Quit the application."""
        try:
            self.cleanup()
            self.quit()
        except Exception as e:
            print(f"Error during quit: {e}")
            import sys
            sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.hotkey_manager:
                self.hotkey_manager.stop()
        except Exception as e:
            print(f"Hotkey cleanup error: {e}")
        
        try:
            if self.analysis_thread and self.analysis_thread.isRunning():
                self.analysis_thread.quit()
                if not self.analysis_thread.wait(2000):  # 2 second timeout
                    self.analysis_thread.terminate()
        except Exception as e:
            print(f"Thread cleanup error: {e}")
        
        try:
            if hasattr(self, 'context_window') and self.context_window:
                self.context_window.close()
        except Exception as e:
            print(f"Context window cleanup error: {e}")

def main():
    """Main entry point."""
    # Enable high DPI support (these attributes were removed in PyQt6)
    # High DPI is enabled by default in PyQt6
    pass
    
    # Create application
    app = BSMApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("BSM")
    app.setApplicationDisplayName("BullShit Meter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BSM Development")
    
    # Prevent application from quitting when windows are closed
    app.setQuitOnLastWindowClosed(False)
    
    # Handle system signals
    def signal_handler(signum, frame):
        app.quit_application()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        app.quit_application()

if __name__ == "__main__":
    main()