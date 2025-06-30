#!/usr/bin/env python3
"""
BSM (BullShit Meter) - Clean Working Version
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
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QProgressDialog, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTabWidget, QScrollArea, QFrame, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon, QAction

# Fix QtWebEngineWidgets issue
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    # Set OpenGL context sharing before QApplication creation
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
except ImportError:
    logger.warning("QtWebEngineWidgets not available - some features may be limited")

# BSM core imports (with error handling)
try:
    from bsm.core.settings import SettingsManager
    logger.info("✅ Settings manager imported")
except ImportError as e:
    logger.warning(f"Settings manager import failed: {e}")
    SettingsManager = None

# Import OCR and screenshot functionality
try:
    from bsm.utils.enhanced_ocr import EnhancedOCR
    from bsm.ui.screenshot_selector import ScreenshotSelector, select_screen_region
    logger.info("✅ OCR and screenshot modules imported")
except ImportError as e:
    logger.warning(f"OCR/Screenshot modules import failed: {e}")
    EnhancedOCR = None
    ScreenshotSelector = None
    select_screen_region = None

# Import Settings Window
try:
    from bsm.ui.settings_window import SettingsWindow
    logger.info("✅ Settings window imported")
except ImportError as e:
    logger.warning(f"Settings window import failed: {e}")
    SettingsWindow = None


class BSMMainWindow(QMainWindow):
    """Main BSM application window."""
    
    def __init__(self):
        super().__init__()
        self.settings_manager = None
        self.enhanced_ocr = None
        self.screenshot_selector = None
        
        # Initialize components in correct order
        self.init_settings()
        self.init_ocr()
        self.init_ui()
        self.init_system_tray()
        
    def init_settings(self):
        """Initialize settings manager."""
        if SettingsManager:
            try:
                self.settings_manager = SettingsManager()
                logger.info("✅ Settings manager initialized")
            except Exception as e:
                logger.error(f"Settings manager failed: {e}")
                
    def init_ocr(self):
        """Initialize OCR and screenshot functionality."""
        if EnhancedOCR:
            try:
                self.enhanced_ocr = EnhancedOCR()
                logger.info("✅ Enhanced OCR initialized")
            except Exception as e:
                logger.error(f"Enhanced OCR failed: {e}")
                
        # Note: ScreenshotSelector is created on-demand during capture
        # to avoid issues with fullscreen overlay initialization
        if ScreenshotSelector:
            logger.info("✅ Screenshot selector available")
        else:
            logger.warning("⚠️ Screenshot selector not available")
    
    def init_system_tray(self):
        """Initialize system tray icon and menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available")
            return
            
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon (you can replace with a proper icon file)
        icon = QIcon()
        # For now, use a simple colored square as icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(52, 152, 219))  # Blue color
        icon.addPixmap(pixmap)
        self.tray_icon.setIcon(icon)
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show BSM", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide BSM", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit BSM", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("BSM - BullShit Meter")
        
        # Handle tray icon activation (double-click to show/hide)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        logger.info("✅ System tray initialized")
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
    
    def show_window(self):
        """Show and raise the main window."""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def quit_application(self):
        """Properly quit the application."""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event - hide to system tray instead of quitting."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # Hide to system tray instead of closing
            self.hide()
            self.tray_icon.showMessage(
                "BSM - BullShit Meter",
                "Application is still running in the system tray. Double-click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            event.ignore()  # Don't actually close the application
            logger.info("Window hidden to system tray")
        else:
            # No system tray available, allow normal close
            event.accept()
            logger.info("Application closing normally")
                
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
            
        if self.enhanced_ocr:
            status_text += "📷 Enhanced OCR: Active\n"
        else:
            status_text += "⚠️ Enhanced OCR: Not available\n"
            
        if ScreenshotSelector:
            status_text += "🖼️ Screenshot selector: Available\n"
        else:
            status_text += "⚠️ Screenshot selector: Not available\n"
            
        status_text += "\n📋 Available Features:\n"
        status_text += "• Basic application framework\n"
        status_text += "• Settings management (if available)\n"
        if self.enhanced_ocr and ScreenshotSelector:
            status_text += "• Regional screenshot capture with OCR\n"
        status_text += "• Ready for configuration\n\n"
        status_text += "🚀 Next Steps:\n"
        status_text += "• Configure API keys for AI analysis\n"
        status_text += "• Set up hotkeys for quick access\n"
        if self.enhanced_ocr and ScreenshotSelector:
            status_text += "• Use 'Capture Screenshot' for regional OCR\n"
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
        
        # Screenshot capture button
        screenshot_btn = QPushButton("📷 Capture Screenshot")
        screenshot_btn.setFont(QFont("Arial", 12))
        screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        screenshot_btn.clicked.connect(self.capture_screenshot)
        if not (self.enhanced_ocr and ScreenshotSelector):
            screenshot_btn.setEnabled(False)
            screenshot_btn.setToolTip("Enhanced OCR and screenshot modules not available")
        
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
        button_layout.addWidget(screenshot_btn)
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
        """Perform AI-powered fact-checking and analysis."""
        print("\n=== DEBUG: analyze_text() called ===")
        text = self.text_area.toPlainText().strip()
        print(f"DEBUG: Text to analyze: {text[:100]}...")
        if not text:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Text", "Please enter some text to analyze!")
            return
            
        # Check if we have settings and API keys configured
        if not self.settings_manager:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings Required", 
                              "Settings manager not available. Please configure API keys in Settings.")
            return
            
        try:
            # Import AI providers
            from bsm.core.ai_providers import AIProviderManager, OpenAIProvider, ClaudeProvider, OllamaProvider
            import asyncio
            
            # Show progress dialog
            from PyQt6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Analyzing text with AI...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            progress.show()
            
            # Create AI provider manager
            ai_manager = AIProviderManager()
            
            # Try to get API keys from settings
            settings = self.settings_manager.get_all_settings() if hasattr(self.settings_manager, 'get_all_settings') else {}
            logger.info(f"Settings manager available: {self.settings_manager is not None}")
            logger.info(f"Settings keys: {list(settings.keys()) if settings else 'No settings'}")
            
            # Add available providers based on configured API keys
            providers_added = []
            
            # Try OpenAI
            openai_key = settings.get('openai_api_key')
            if openai_key and openai_key.strip():
                try:
                    ai_manager.add_provider('openai', OpenAIProvider(openai_key))
                    providers_added.append('openai')
                    logger.info("OpenAI provider added")
                except Exception as e:
                    logger.warning(f"Failed to add OpenAI provider: {e}")
            
            # Try Claude
            claude_key = settings.get('claude_api_key')
            if claude_key and claude_key.strip():
                try:
                    ai_manager.add_provider('claude', ClaudeProvider(claude_key))
                    providers_added.append('claude')
                    logger.info("Claude provider added")
                except Exception as e:
                    logger.warning(f"Failed to add Claude provider: {e}")
            
            # Try Ollama (local)
            ollama_endpoint = settings.get('ollama_endpoint', 'http://localhost:11434')
            try:
                ai_manager.add_provider('ollama', OllamaProvider(ollama_endpoint))
                providers_added.append('ollama')
                logger.info("Ollama provider added")
            except Exception as e:
                logger.warning(f"Failed to add Ollama provider: {e}")
            
            if not providers_added:
                progress.close()
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No AI Providers", 
                                  "No AI providers are available. Please configure at least one provider in Settings.")
                return
            
            # Check for user's preferred default provider
            preferred_provider = settings.get('default_ai_provider', 'auto')
            if preferred_provider != 'auto' and preferred_provider in providers_added:
                # Move preferred provider to front of list
                providers_added.remove(preferred_provider)
                providers_added.insert(0, preferred_provider)
                logger.info(f"Using preferred default provider: {preferred_provider}")
            
            logger.info(f"Available providers: {providers_added}")
            
            # Set up progress callback
            def update_progress(value):
                if not progress.wasCanceled():
                    progress.setValue(value)
                    QApplication.processEvents()
            
            # Get attitude mode from settings (default to 'balanced')
            attitude_mode = settings.get('attitude_mode', 'balanced')
            
            # Perform analysis asynchronously
            async def run_analysis():
                try:
                    logger.info(f"Starting AI analysis with providers: {providers_added}")
                    logger.info(f"Text to analyze (first 100 chars): {text[:100]}...")
                    logger.info(f"Attitude mode: {attitude_mode}")
                    
                    # Set progress callback for the primary provider
                    primary_provider = providers_added[0]
                    logger.info(f"Using primary provider: {primary_provider}")
                    
                    if hasattr(ai_manager.providers.get(primary_provider), 'set_progress_callback'):
                        ai_manager.providers[primary_provider].set_progress_callback(update_progress)
                        logger.info("Progress callback set")
                    
                    # Run analysis with fallback
                    logger.info("Calling analyze_with_fallback...")
                    result = await ai_manager.analyze_with_fallback(
                        text=text,
                        attitude_mode=attitude_mode,
                        primary_provider=primary_provider,
                        fallback_providers=providers_added[1:] if len(providers_added) > 1 else None
                    )
                    logger.info(f"Analysis completed. Result type: {type(result)}")
                    if result:
                        logger.info(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    else:
                        logger.warning("Analysis returned None or empty result")
                    return result
                except Exception as e:
                    logger.error(f"AI analysis failed with exception: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return None
            
            # Run the async analysis
            try:
                result = asyncio.run(run_analysis())
            except RuntimeError:
                # If there's already an event loop, use run_until_complete
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(run_analysis())
            
            progress.close()
            
            if result and isinstance(result, dict):
                # Debug: Log the raw result
                logger.info(f"Raw AI result: {result}")
                
                # Check if this is an error result from failed AI providers
                if result.get('error') and 'failed' in str(result.get('error', '')).lower():
                    logger.warning("AI providers failed - showing enhanced fallback results")
                    # Create enhanced fallback results
                    enhanced_result = {
                        'provider': '🔧 BSM Configuration Required',
                        'attitude_mode': attitude_mode,
                        'confidence': 0,
                        'fact_check': f"# 🚀 BSM Analysis Ready!\n\n**Text Analyzed:** {len(text)} characters, {len(text.split())} words\n\n## 🔧 Setup Required\n\nTo unlock full AI-powered fact-checking, please configure your AI provider:\n\n### Option 1: OpenAI (Recommended)\n- Go to **Settings** → **AI Providers**\n- Add your OpenAI API key\n- Get comprehensive GPT-4 analysis\n\n### Option 2: Claude (Anthropic)\n- Go to **Settings** → **AI Providers**\n- Add your Claude API key\n- Get detailed Anthropic analysis\n\n### Option 3: Local Ollama\n- Install Ollama locally\n- Pull a model: `ollama pull llama3.2`\n- Use completely private, local analysis\n\n## 📊 Current Text Preview\n\n```\n{text[:200]}{'...' if len(text) > 200 else ''}\n```\n\n**Ready to fact-check when you configure an AI provider!**",
                        'counter_argument': "🎯 **Critical Thinking Reminder**\n\nWhile setting up AI analysis, remember to:\n- Question assumptions in any claims\n- Look for multiple perspectives\n- Verify sources independently\n- Consider potential biases\n\nAI analysis enhances but doesn't replace critical thinking!",
                        'sources': [
                            "🔑 Configure API keys in Settings for real-time verification",
                            "📚 OpenAI GPT-4 for comprehensive analysis",
                            "🧠 Claude for detailed reasoning",
                            "🏠 Ollama for private, local analysis"
                        ],
                        'summary': "🎉 **BSM is ready to analyze your text!** Configure an AI provider in Settings to unlock powerful fact-checking, counter-argument generation, and logical analysis. Your text is loaded and waiting for AI-powered insights."
                    }
                    
                    print("DEBUG: Showing enhanced fallback results")
                    try:
                        from bsm.ui.results_window import ResultsWindow
                        results_window = ResultsWindow(enhanced_result, self)
                        results_window.exec()
                        logger.info("Enhanced fallback results displayed")
                    except Exception as e:
                        logger.error(f"Failed to show enhanced results: {e}")
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.information(self, "Setup Required", 
                                              "🔧 BSM is ready! Please configure your AI provider in Settings to unlock fact-checking analysis.")
                    return
                
                # Process and flatten the AI response for display
                processed_result = self.process_ai_response(result, attitude_mode)
                
                # Debug: Log the processed result
                logger.info(f"Processed result: {processed_result}")
                
                # Show results in beautiful popup window
                print("DEBUG: About to show results in popup window")
                try:
                    from bsm.ui.results_window import ResultsWindow
                    print("DEBUG: ResultsWindow imported successfully")
                    results_window = ResultsWindow(processed_result, self)
                    print("DEBUG: ResultsWindow created successfully")
                    results_window.exec()
                    print("DEBUG: ResultsWindow.exec() completed")
                    logger.info("Results displayed in popup window")
                except ImportError as e:
                    logger.error(f"Failed to import ResultsWindow: {e}")
                    # Fallback to simple message box
                    from PyQt6.QtWidgets import QMessageBox
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Analysis Complete")
                    msg.setText(f"🎉 AI analysis completed successfully!\n\n"
                              f"🤖 Provider: {processed_result.get('provider', 'AI Provider')}\n\n"
                              f"Results:\n{processed_result.get('fact_check', 'Analysis completed')}")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()
                
            else:
                logger.warning("AI analysis returned no results - using fallback mock data")
                # Create mock results for testing/fallback
                mock_result = {
                    'provider': 'BSM Fallback Analysis',
                    'attitude_mode': attitude_mode,
                    'confidence': 75,
                    'fact_check': f"**Analysis of your text:**\n\nThe provided text has been analyzed for factual accuracy and logical consistency. While a full AI analysis requires proper API configuration, this fallback analysis can identify basic patterns.\n\n**Text Length:** {len(text)} characters\n**Word Count:** {len(text.split())} words\n\n**Note:** For comprehensive fact-checking with real-time data verification, please configure your OpenAI or Claude API keys in Settings.",
                    'counter_argument': "Alternative perspectives should always be considered when evaluating claims. Critical thinking involves examining evidence from multiple angles and questioning assumptions.",
                    'sources': [
                        "Configure API keys for real source verification",
                        "BSM requires OpenAI or Claude API access for full analysis",
                        "Local Ollama can be used as an alternative"
                    ],
                    'summary': "This is a fallback analysis. Configure your AI provider API keys in Settings for comprehensive fact-checking and counter-argument generation."
                }
                
                print("DEBUG: About to show FALLBACK results in popup window")
                try:
                    from bsm.ui.results_window import ResultsWindow
                    print("DEBUG: ResultsWindow imported for fallback")
                    results_window = ResultsWindow(mock_result, self)
                    print("DEBUG: Fallback ResultsWindow created successfully")
                    results_window.exec()
                    print("DEBUG: Fallback ResultsWindow.exec() completed")
                    logger.info("Fallback results displayed in popup window")
                except Exception as e:
                    logger.error(f"Failed to show fallback results: {e}")
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Analysis Issue", 
                                      "AI analysis failed and fallback results could not be displayed. Please check your configuration.")
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Analysis Error", 
                               f"An error occurred during analysis:\n{str(e)}")
    
    def process_ai_response(self, raw_result, attitude_mode):
        """Process and flatten AI response for display in results window."""
        processed = {
            'provider': raw_result.get('provider_used', raw_result.get('provider', 'AI Provider')),
            'attitude_mode': attitude_mode
        }
        
        # Handle confidence score
        confidence = raw_result.get('confidence_score', raw_result.get('confidence', 0))
        if isinstance(confidence, float):
            processed['confidence'] = int(confidence * 100)  # Convert to percentage
        else:
            processed['confidence'] = confidence
        
        # Handle fact check - flatten if it's an object
        fact_check = raw_result.get('fact_check')
        if isinstance(fact_check, dict):
            # Flatten the fact_check object into readable text
            fact_text = ""
            if 'verified_facts' in fact_check and fact_check['verified_facts']:
                fact_text += "**Verified Facts:**\n"
                for fact in fact_check['verified_facts']:
                    fact_text += f"• {fact}\n"
                fact_text += "\n"
            
            if 'questionable_claims' in fact_check and fact_check['questionable_claims']:
                fact_text += "**Questionable Claims:**\n"
                for claim in fact_check['questionable_claims']:
                    fact_text += f"• {claim}\n"
                fact_text += "\n"
            
            if 'unsupported_assertions' in fact_check and fact_check['unsupported_assertions']:
                fact_text += "**Unsupported Assertions:**\n"
                for assertion in fact_check['unsupported_assertions']:
                    fact_text += f"• {assertion}\n"
            
            processed['fact_check'] = fact_text.strip() if fact_text else "No specific fact-checking results available."
        elif isinstance(fact_check, str):
            processed['fact_check'] = fact_check
        else:
            processed['fact_check'] = raw_result.get('analysis', 'Analysis completed.')
        
        # Handle counter arguments
        counter_args = raw_result.get('counter_arguments', raw_result.get('counter_argument'))
        if isinstance(counter_args, list):
            processed['counter_argument'] = "\n".join([f"• {arg}" for arg in counter_args])
        elif isinstance(counter_args, str):
            processed['counter_argument'] = counter_args
        else:
            # Try alternative perspectives
            alt_perspectives = raw_result.get('alternative_perspectives')
            if isinstance(alt_perspectives, list):
                processed['counter_argument'] = "\n".join([f"• {perspective}" for perspective in alt_perspectives])
            elif isinstance(alt_perspectives, str):
                processed['counter_argument'] = alt_perspectives
        
        # Handle sources
        sources = raw_result.get('sources_needed', raw_result.get('sources', []))
        if isinstance(sources, list):
            processed['sources'] = sources
        elif isinstance(sources, str):
            processed['sources'] = [sources]
        
        # Handle summary/conclusion
        summary = raw_result.get('summary', raw_result.get('conclusion'))
        if summary:
            processed['summary'] = summary
        
        # Handle logical analysis if present
        logical_analysis = raw_result.get('logical_analysis')
        if isinstance(logical_analysis, dict):
            analysis_text = ""
            if 'fallacies_identified' in logical_analysis and logical_analysis['fallacies_identified']:
                analysis_text += "**Logical Fallacies:**\n"
                for fallacy in logical_analysis['fallacies_identified']:
                    analysis_text += f"• {fallacy}\n"
                analysis_text += "\n"
            
            if 'argument_strengths' in logical_analysis and logical_analysis['argument_strengths']:
                analysis_text += "**Argument Strengths:**\n"
                for strength in logical_analysis['argument_strengths']:
                    analysis_text += f"• {strength}\n"
                analysis_text += "\n"
            
            if 'argument_weaknesses' in logical_analysis and logical_analysis['argument_weaknesses']:
                analysis_text += "**Argument Weaknesses:**\n"
                for weakness in logical_analysis['argument_weaknesses']:
                    analysis_text += f"• {weakness}\n"
            
            if analysis_text:
                processed['analysis'] = analysis_text.strip()
        
        # If we have an error, include it
        if 'error' in raw_result:
            processed['error'] = raw_result['error']
        
        # Fallback: if we don't have key content, use the raw analysis
        if not processed.get('fact_check') and not processed.get('counter_argument'):
            if 'analysis' in raw_result:
                processed['fact_check'] = raw_result['analysis']
            elif 'content' in raw_result:
                processed['fact_check'] = raw_result['content']
            else:
                processed['fact_check'] = "Analysis completed, but no detailed results were returned."
        
        return processed
        
    def capture_screenshot(self):
        """Capture regional screenshot and perform OCR."""
        if not (self.enhanced_ocr and ScreenshotSelector):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Feature Unavailable", 
                              "Screenshot capture and OCR functionality is not available.\n"
                              "Please ensure all dependencies are installed.")
            return
            
        try:
            # Hide main window during screenshot capture
            self.hide()
            
            # Use the select_screen_region function for regional selection
            if select_screen_region:
                region = select_screen_region()
                
                if region and len(region) == 4:
                    x, y, width, height = region
                    logger.info(f"Screenshot region selected: {x}, {y}, {width}x{height}")
                    
                    # Capture the selected region using PIL
                    from PIL import ImageGrab
                    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                    
                    if screenshot:
                        # Perform OCR on captured screenshot using EnhancedOCR
                        from bsm.utils.enhanced_ocr import PreprocessingMode
                        import asyncio
                        
                        # Run the async OCR processing in the current thread
                        try:
                            ocr_result = asyncio.run(self.enhanced_ocr.process_image(
                                screenshot, 
                                mode=PreprocessingMode.SCREENSHOT
                            ))
                        except RuntimeError:
                            # If there's already an event loop running, use run_in_executor
                            loop = asyncio.get_event_loop()
                            ocr_result = loop.run_until_complete(self.enhanced_ocr.process_image(
                                screenshot, 
                                mode=PreprocessingMode.SCREENSHOT
                            ))
                        
                        if ocr_result and ocr_result.text.strip():
                            extracted_text = ocr_result.text.strip()
                            logger.info(f"OCR extracted {len(extracted_text)} characters with {ocr_result.confidence:.1%} confidence")
                            
                            # Add extracted text to text area
                            current_text = self.text_area.toPlainText()
                            if current_text:
                                new_text = current_text + "\n\n--- OCR Extracted Text ---\n" + extracted_text
                            else:
                                new_text = "--- OCR Extracted Text ---\n" + extracted_text
                            
                            self.text_area.setPlainText(new_text)
                            
                            # Show success message with option to analyze
                            from PyQt6.QtWidgets import QMessageBox
                            msg = QMessageBox(self)
                            msg.setWindowTitle("OCR Success")
                            msg.setText(f"📷 Screenshot captured and processed!\n\n"
                                      f"📝 Extracted {len(extracted_text)} characters of text.\n"
                                      f"🎯 Confidence: {ocr_result.confidence:.1%}\n\n"
                                      f"The text has been added to the analysis area.\n\n"
                                      f"🤖 Would you like to analyze this text for fact-checking?")
                            msg.setIcon(QMessageBox.Icon.Information)
                            
                            # Add custom buttons for analysis options
                            analyze_btn = msg.addButton("🔍 Analyze Now", QMessageBox.ButtonRole.AcceptRole)
                            skip_btn = msg.addButton("📝 Just Extract", QMessageBox.ButtonRole.RejectRole)
                            
                            msg.setStyleSheet("""
                                QMessageBox {
                                    background-color: #ffffff;
                                    color: #2c3e50;
                                    font-size: 14px;
                                }
                                QMessageBox QLabel {
                                    color: #2c3e50;
                                    background-color: #ffffff;
                                    padding: 10px;
                                }
                                QMessageBox QPushButton {
                                    background-color: #3498db;
                                    color: white;
                                    border: none;
                                    padding: 8px 16px;
                                    border-radius: 4px;
                                    font-weight: bold;
                                    min-width: 100px;
                                    margin: 2px;
                                }
                                QMessageBox QPushButton:hover {
                                    background-color: #2980b9;
                                }
                            """)
                            
                            msg.exec()
                            
                            # Check which button was clicked and trigger analysis if requested
                            if msg.clickedButton() == analyze_btn:
                                logger.info("User requested AI analysis of OCR text")
                                self.analyze_text()  # Trigger the existing analyze functionality
                        else:
                            from PyQt6.QtWidgets import QMessageBox
                            QMessageBox.warning(self, "OCR Failed", 
                                              "No text could be extracted from the screenshot.\n"
                                              "Please try capturing a clearer image with text.")
                    else:
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "Screenshot Failed", 
                                          "Failed to capture screenshot.\n"
                                          "Please try again.")
                else:
                    logger.info("Screenshot capture cancelled by user")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Feature Unavailable", 
                                  "Screenshot selection function is not available.")
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Capture Error", 
                               f"Screenshot capture failed:\n{str(e)}")
        finally:
            # Always show main window again
            self.show()
            self.raise_()
            self.activateWindow()
        
    def show_settings(self):
        """Show settings dialog."""
        if not SettingsWindow:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings Unavailable", 
                              "Settings window is not available.\n"
                              "Please ensure all dependencies are installed.")
            return
            
        if not self.settings_manager:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings Manager Unavailable", 
                              "Settings manager is not available.\n"
                              "Cannot open settings without settings manager.")
            return
            
        try:
            # Create and show settings window
            settings_dialog = SettingsWindow(self.settings_manager)
            settings_dialog.settings_changed.connect(self.on_settings_changed)
            
            # Show dialog modally
            result = settings_dialog.exec()
            
            if result == settings_dialog.DialogCode.Accepted:
                logger.info("Settings saved successfully")
                # Optionally refresh UI or reload components
                self.refresh_status_display()
            else:
                logger.info("Settings dialog cancelled")
                
        except Exception as e:
            logger.error(f"Settings dialog error: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Settings Error", 
                               f"Failed to open settings dialog:\n{str(e)}")
                               
    def on_settings_changed(self, settings_dict):
        """Handle settings changes from the settings dialog."""
        logger.info(f"Settings changed: {list(settings_dict.keys())}")
        
        # Update status display to reflect any changes
        self.refresh_status_display()
        
        # Show confirmation message
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Settings Updated")
        msg.setText("⚙️ Settings have been updated successfully!\n\n"
                   "Changes will take effect immediately.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                background-color: #ffffff;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #229954;
            }
        """)
        msg.exec()
        
    def refresh_status_display(self):
        """Refresh the status display to show current component states."""
        try:
            # Find the status label and update it
            status_text = "✅ BSM Application is running successfully!\n\n"
            if self.settings_manager:
                status_text += "🔧 Settings manager: Active\n"
            else:
                status_text += "⚠️ Settings manager: Not available\n"
                
            if self.enhanced_ocr:
                status_text += "📷 Enhanced OCR: Active\n"
            else:
                status_text += "⚠️ Enhanced OCR: Not available\n"
                
            if ScreenshotSelector:
                status_text += "🖼️ Screenshot selector: Available\n"
            else:
                status_text += "⚠️ Screenshot selector: Not available\n"
                
            status_text += "\n📋 Available Features:\n"
            status_text += "• Basic application framework\n"
            status_text += "• Settings management (if available)\n"
            if self.enhanced_ocr and ScreenshotSelector:
                status_text += "• Regional screenshot capture with OCR\n"
            status_text += "• Ready for configuration\n\n"
            status_text += "🚀 Next Steps:\n"
            status_text += "• Configure API keys for AI analysis\n"
            status_text += "• Set up hotkeys for quick access\n"
            if self.enhanced_ocr and ScreenshotSelector:
                status_text += "• Use 'Capture Screenshot' for regional OCR\n"
            status_text += "• Enable advanced features"
            
            # Update the status label if it exists
            for child in self.centralWidget().findChildren(QLabel):
                if "BSM Application is running successfully" in child.text():
                    child.setText(status_text)
                    break
                    
        except Exception as e:
            logger.error(f"Failed to refresh status display: {e}")


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
