"""
Context input window for adding perspective and context to analysis.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel, 
                             QComboBox, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ContextWindow(QDialog):
    """Window for adding context and perspective to analysis."""
    
    analysis_requested = pyqtSignal(str, dict)  # text, context_data
    
    def __init__(self, text: str, source_type: str):
        super().__init__()
        self.text = text
        self.source_type = source_type
        self.init_ui()
        self.setup_styling()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BSM - Add Context for Analysis")
        
        # Simple window setup without complex flags
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        
        # Center on screen with larger size
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # Make it larger and resizable
        width, height = 800, 700
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(600, 500)  # Allow resizing but set minimum
        
        layout = QVBoxLayout(self)
        
        # Preview of text being analyzed
        preview_group = QGroupBox("Text to Analyze")
        preview_layout = QVBoxLayout(preview_group)
        
        self.text_preview = QTextEdit()
        
        # Clean and format text for preview
        preview_text = self.text.strip()
        if len(preview_text) > 300:
            # Find a good break point (sentence end, period, etc.)
            break_point = 300
            for i in range(250, min(350, len(preview_text))):
                if preview_text[i] in '.!?\n':
                    break_point = i + 1
                    break
            preview_text = preview_text[:break_point].strip() + "..."
        
        self.text_preview.setPlainText(preview_text)
        self.text_preview.setMinimumHeight(150)
        self.text_preview.setMaximumHeight(200)
        self.text_preview.setReadOnly(True)
        
        # Set font size for better readability
        font = self.text_preview.font()
        font.setPointSize(12)
        self.text_preview.setFont(font)
        preview_layout.addWidget(self.text_preview)
        
        layout.addWidget(preview_group)
        
        # Context settings
        context_group = QGroupBox("Analysis Context")
        context_layout = QFormLayout(context_group)
        context_layout.setVerticalSpacing(15)
        context_layout.setHorizontalSpacing(20)
        
        # User perspective
        self.perspective_combo = QComboBox()
        self.perspective_combo.addItems([
            "Neutral Observer",
            "My Perspective", 
            "Counter-Perspective",
            "Expert Analysis",
            "Specific Person..."
        ])
        self.perspective_combo.setMinimumHeight(35)
        context_layout.addRow("Analyze From:", self.perspective_combo)
        
        # Custom perspective name
        self.custom_perspective = QLineEdit()
        self.custom_perspective.setPlaceholderText("e.g., 'John Smith' or 'Tech Expert'")
        self.custom_perspective.setEnabled(False)
        self.custom_perspective.setMinimumHeight(35)
        context_layout.addRow("Custom Name:", self.custom_perspective)
        
        # Context prompt
        self.context_prompt = QTextEdit()
        self.context_prompt.setPlaceholderText(
            "Optional: Add any additional context...\n\n"
            "Examples:\n"
            "• This is a conversation between me and my boss\n" 
            "• I need to respond to this email professionally\n"
            "• Analyze this from a technical perspective\n"
            "• Check if this marketing claim is accurate"
        )
        self.context_prompt.setMinimumHeight(120)
        self.context_prompt.setMaximumHeight(150)
        context_layout.addRow("Additional Context:", self.context_prompt)
        
        layout.addWidget(context_group)
        
        # User profile section
        profile_group = QGroupBox("My Profile (Optional)")
        profile_layout = QFormLayout(profile_group)
        profile_layout.setVerticalSpacing(15)
        profile_layout.setHorizontalSpacing(20)
        
        self.user_name = QLineEdit()
        self.user_name.setPlaceholderText("Your name or role")
        self.user_name.setMinimumHeight(35)
        profile_layout.addRow("Name/Role:", self.user_name)
        
        self.user_expertise = QLineEdit()
        self.user_expertise.setPlaceholderText("e.g., Software Developer, Marketing Manager")
        self.user_expertise.setMinimumHeight(35)
        profile_layout.addRow("Expertise:", self.user_expertise)
        
        self.save_profile = QCheckBox("Save as default profile")
        self.save_profile.setMinimumHeight(25)
        profile_layout.addRow("", self.save_profile)
        
        layout.addWidget(profile_group)
        
        # Analysis preferences
        prefs_group = QGroupBox("Analysis Preferences")
        prefs_layout = QFormLayout(prefs_group)
        prefs_layout.setVerticalSpacing(15)
        prefs_layout.setHorizontalSpacing(20)
        
        self.analysis_mode = QComboBox()
        self.analysis_mode.addItems([
            "balanced", "argumentative", "helpful"
        ])
        self.analysis_mode.setMinimumHeight(35)
        prefs_layout.addRow("Attitude:", self.analysis_mode)
        
        self.include_sources = QCheckBox("Include source verification")
        self.include_sources.setChecked(True)
        prefs_layout.addRow("", self.include_sources)
        
        self.include_counter = QCheckBox("Include counter-arguments")
        self.include_counter.setChecked(True)
        prefs_layout.addRow("", self.include_counter)
        
        layout.addWidget(prefs_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.quick_analyze_btn = QPushButton("Quick Analyze")
        self.quick_analyze_btn.clicked.connect(self.quick_analyze)
        button_layout.addWidget(self.quick_analyze_btn)
        
        self.analyze_btn = QPushButton("Analyze with Context")
        self.analyze_btn.clicked.connect(self.analyze_with_context)
        self.analyze_btn.setDefault(True)
        button_layout.addWidget(self.analyze_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.perspective_combo.currentTextChanged.connect(self.on_perspective_changed)
    
    def on_perspective_changed(self, text):
        """Handle perspective selection change."""
        self.custom_perspective.setEnabled(text == "Specific Person...")
        if text == "Specific Person...":
            self.custom_perspective.setFocus()
    
    def quick_analyze(self):
        """Perform quick analysis without additional context."""
        context_data = {
            'perspective': 'neutral',
            'attitude_mode': 'balanced',
            'context_prompt': '',
            'source_type': self.source_type
        }
        self.analysis_requested.emit(self.text, context_data)
        self.accept()
    
    def analyze_with_context(self):
        """Perform analysis with full context."""
        perspective = self.perspective_combo.currentText()
        if perspective == "Specific Person...":
            perspective = self.custom_perspective.text() or "Custom Perspective"
        
        context_data = {
            'perspective': perspective,
            'attitude_mode': self.analysis_mode.currentText(),
            'context_prompt': self.context_prompt.toPlainText(),
            'user_name': self.user_name.text(),
            'user_expertise': self.user_expertise.text(),
            'include_sources': self.include_sources.isChecked(),
            'include_counter': self.include_counter.isChecked(),
            'source_type': self.source_type,
            'save_profile': self.save_profile.isChecked()
        }
        
        self.analysis_requested.emit(self.text, context_data)
        self.accept()
    
    def setup_styling(self):
        """Setup window styling with dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 15px;
                background-color: #333333;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
            }
            
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #555555;
                border-radius: 6px;
                background-color: #404040;
                color: #ffffff;
                font-size: 13px;
                selection-background-color: #4CAF50;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
                background-color: #4a4a4a;
            }
            
            QTextEdit[readOnly="true"] {
                background-color: #363636;
                color: #cccccc;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:default {
                background-color: #2196F3;
            }
            
            QPushButton:default:hover {
                background-color: #1976D2;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
                font-size: 13px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #404040;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            
            QFormLayout QLabel {
                color: #cccccc;
                font-weight: normal;
            }
        """)