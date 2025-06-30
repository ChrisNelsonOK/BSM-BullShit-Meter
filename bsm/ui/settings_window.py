from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QTabWidget, QWidget,
                             QLabel, QFileDialog, QCheckBox, QSpinBox, QTextEdit,
                             QGroupBox, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any

class SettingsWindow(QDialog):
    """Settings configuration window."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BSM Settings")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_api_tab()
        self.create_behavior_tab()
        self.create_hotkey_tab()
        self.create_database_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_button = QPushButton("Test APIs")
        self.test_button.clicked.connect(self.test_apis)
        button_layout.addWidget(self.test_button)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setup_styling()
    
    def create_api_tab(self):
        """Create API configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # OpenAI API
        openai_group = QGroupBox("OpenAI API")
        openai_layout = QFormLayout(openai_group)
        
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.openai_key_edit.setPlaceholderText("sk-...")
        openai_layout.addRow("API Key:", self.openai_key_edit)
        
        layout.addWidget(openai_group)
        
        # Claude API
        claude_group = QGroupBox("Claude API")
        claude_layout = QFormLayout(claude_group)
        
        self.claude_key_edit = QLineEdit()
        self.claude_key_edit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.claude_key_edit.setPlaceholderText("sk-ant-...")
        claude_layout.addRow("API Key:", self.claude_key_edit)
        
        layout.addWidget(claude_group)
        
        # Ollama
        ollama_group = QGroupBox("Ollama (Local LLM)")
        ollama_layout = QFormLayout(ollama_group)
        
        self.ollama_endpoint_edit = QLineEdit()
        self.ollama_endpoint_edit.setPlaceholderText("http://localhost:11434")
        ollama_layout.addRow("Endpoint:", self.ollama_endpoint_edit)
        
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.setPlaceholderText("llama2")
        
        # Add refresh button next to model dropdown
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.ollama_model_combo)
        
        self.refresh_models_button = QPushButton("🔄")
        self.refresh_models_button.setFixedSize(35, 35)
        self.refresh_models_button.setToolTip("Refresh available models")
        self.refresh_models_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                border: 1px solid #666666;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
            }
        """)
        self.refresh_models_button.clicked.connect(self.refresh_ollama_models)
        model_layout.addWidget(self.refresh_models_button)
        
        ollama_layout.addRow("Model:", model_layout)
        
        layout.addWidget(ollama_group)
        
        # Default Provider Selection
        default_group = QGroupBox("Default AI Provider")
        default_layout = QFormLayout(default_group)
        
        self.default_provider_combo = QComboBox()
        self.default_provider_combo.addItems([
            "auto",      # Auto-select based on availability
            "openai",    # OpenAI GPT
            "claude",    # Claude
            "ollama"     # Local Ollama
        ])
        self.default_provider_combo.setToolTip(
            "Choose your preferred AI provider. 'auto' will use the first available provider."
        )
        default_layout.addRow("Preferred Provider:", self.default_provider_combo)
        
        # Add explanation label
        explanation = QLabel(
            "💡 The selected provider will be used first for AI analysis. "
            "If unavailable, BSM will fallback to other configured providers."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #888888; font-size: 11px; margin: 5px;")
        default_layout.addRow(explanation)
        
        layout.addWidget(default_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "API Keys")
    
    def create_behavior_tab(self):
        """Create behavior configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # LLM Provider
        provider_group = QGroupBox("LLM Provider")
        provider_layout = QFormLayout(provider_group)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["openai", "claude", "ollama"])
        provider_layout.addRow("Primary Provider:", self.llm_provider_combo)
        
        layout.addWidget(provider_group)
        
        # Attitude Mode
        attitude_group = QGroupBox("Analysis Attitude")
        attitude_layout = QFormLayout(attitude_group)
        
        self.attitude_combo = QComboBox()
        self.attitude_combo.addItems(["balanced", "argumentative", "helpful"])
        attitude_layout.addRow("Default Mode:", self.attitude_combo)
        
        # Add descriptions
        attitude_desc = QLabel("""• Balanced: Objective analysis with neutral tone
• Argumentative: Aggressive fact-checking, finds flaws
• Helpful: Educational tone, constructive feedback""")
        attitude_desc.setObjectName("description")
        attitude_layout.addRow("", attitude_desc)
        
        layout.addWidget(attitude_group)
        
        # Features
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)
        
        self.auto_save_check = QCheckBox("Auto-save analysis results")
        features_layout.addWidget(self.auto_save_check)
        
        self.show_confidence_check = QCheckBox("Show confidence scores")
        features_layout.addWidget(self.show_confidence_check)
        
        self.enable_ocr_check = QCheckBox("Enable screenshot OCR")
        features_layout.addWidget(self.enable_ocr_check)
        
        layout.addWidget(features_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Behavior")
    
    def create_hotkey_tab(self):
        """Create hotkey configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hotkey_group = QGroupBox("Global Hotkey")
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("ctrl+shift+b")
        hotkey_layout.addRow("Hotkey Combination:", self.hotkey_edit)
        
        # Instructions
        instructions = QLabel("""Hotkey Format Examples:
• ctrl+shift+b
• cmd+shift+b (macOS)  
• alt+f12
• ctrl+alt+space

Use lowercase letters and connect with '+' symbols.
Common modifiers: ctrl, shift, alt, cmd (macOS only)""")
        instructions.setObjectName("description")
        hotkey_layout.addRow("", instructions)
        
        layout.addWidget(hotkey_group)
        
        # Test hotkey button
        test_hotkey_button = QPushButton("Test Hotkey")
        test_hotkey_button.clicked.connect(self.test_hotkey)
        layout.addWidget(test_hotkey_button)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Hotkey")
    
    def create_database_tab(self):
        """Create database configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        db_group = QGroupBox("Database Settings")
        db_layout = QVBoxLayout(db_group)
        
        # Database path
        path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        path_layout.addWidget(self.db_path_edit)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_database_path)
        path_layout.addWidget(browse_button)
        
        db_layout.addLayout(path_layout)
        
        # Database statistics (if available)
        self.db_stats_label = QLabel("Database statistics will appear here")
        self.db_stats_label.setObjectName("description")
        db_layout.addWidget(self.db_stats_label)
        
        layout.addWidget(db_group)
        
        # Database actions
        actions_group = QGroupBox("Database Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        export_button = QPushButton("Export History")
        export_button.clicked.connect(self.export_history)
        actions_layout.addWidget(export_button)
        
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        clear_button.setStyleSheet("color: #d32f2f;")
        actions_layout.addWidget(clear_button)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Database")
    
    def setup_styling(self):
        """Setup window styling with dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #555555;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom: 1px solid #2b2b2b;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #4a4a4a;
            }
            
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                margin: 15px 0;
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
            
            QLineEdit, QComboBox {
                padding: 10px 12px;
                border: 2px solid #555555;
                border-radius: 6px;
                background-color: #404040;
                color: #ffffff;
                font-size: 13px;
                selection-background-color: #4CAF50;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
                background-color: #4a4a4a;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                width: 0px;
                height: 0px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #404040;
                border: 1px solid #555555;
                selection-background-color: #4CAF50;
                color: #ffffff;
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
            
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
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
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTExLjMzMzMgMy41TDUuMjQ5OTkgOS41ODMzM0wyLjY2NjY2IDciIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            
            QCheckBox::indicator:hover {
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
            
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
            }
            
            QScrollBar:vertical {
                background-color: #404040;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #666666;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
            
            /* Special styling for description labels */
            QLabel[objectName="description"] {
                color: #aaaaaa;
                font-size: 11px;
                font-style: italic;
            }
        """)
    
    def load_current_settings(self):
        """Load current settings into the form."""
        # API Keys
        self.openai_key_edit.setText(self.settings_manager.get('api_keys.openai', ''))
        self.claude_key_edit.setText(self.settings_manager.get('api_keys.claude', ''))
        
        # Ollama
        self.ollama_endpoint_edit.setText(self.settings_manager.get('ollama_endpoint', 'http://localhost:11434'))
        
        # Load Ollama models
        self.refresh_ollama_models()
        current_model = self.settings_manager.get('ollama_model', 'llama2')
        self.ollama_model_combo.setCurrentText(current_model)
        
        # Default AI Provider
        default_provider = self.settings_manager.get('default_ai_provider', 'auto')
        self.default_provider_combo.setCurrentText(default_provider)
        
        # Behavior
        self.llm_provider_combo.setCurrentText(self.settings_manager.get('llm_provider', 'openai'))
        self.attitude_combo.setCurrentText(self.settings_manager.get('attitude_mode', 'balanced'))
        
        # Features
        self.auto_save_check.setChecked(self.settings_manager.get('auto_save_results', True))
        self.show_confidence_check.setChecked(self.settings_manager.get('show_confidence_score', True))
        self.enable_ocr_check.setChecked(self.settings_manager.get('enable_screenshot_ocr', True))
        
        # Hotkey
        self.hotkey_edit.setText(self.settings_manager.get('global_hotkey', 'ctrl+shift+b'))
        
        # Database
        self.db_path_edit.setText(self.settings_manager.get_database_path())
        
        # Load database statistics
        self.load_database_stats()
    
    def load_database_stats(self):
        """Load and display database statistics."""
        try:
            from ..core.database import DatabaseManager
            db = DatabaseManager(self.settings_manager.get_database_path())
            stats = db.get_statistics()
            
            stats_text = f"Total analyses: {stats['total_analyses']}"
            if stats['by_attitude_mode']:
                stats_text += f"\n{dict(stats['by_attitude_mode'])}"
            
            self.db_stats_label.setText(stats_text)
        except Exception as e:
            self.db_stats_label.setText(f"Error loading stats: {e}")
    
    def save_settings(self):
        """Save all settings with error handling."""
        try:
            # API Keys
            self.settings_manager.set('api_keys.openai', self.openai_key_edit.text().strip())
            self.settings_manager.set('api_keys.claude', self.claude_key_edit.text().strip())
            
            # Ollama
            self.settings_manager.set('ollama_endpoint', self.ollama_endpoint_edit.text().strip())
            self.settings_manager.set('ollama_model', self.ollama_model_combo.currentText().strip())
            
            # Default AI Provider
            self.settings_manager.set('default_ai_provider', self.default_provider_combo.currentText())
            
            # Behavior
            self.settings_manager.set('llm_provider', self.llm_provider_combo.currentText())
            self.settings_manager.set('attitude_mode', self.attitude_combo.currentText())
            
            # Features
            self.settings_manager.set('auto_save_results', self.auto_save_check.isChecked())
            self.settings_manager.set('show_confidence_score', self.show_confidence_check.isChecked())
            self.settings_manager.set('enable_screenshot_ocr', self.enable_ocr_check.isChecked())
            
            # Hotkey
            self.settings_manager.set('global_hotkey', self.hotkey_edit.text().strip())
            
            # Save to file
            self.settings_manager.save_settings()
            
            # Emit signal with all settings safely
            try:
                self.settings_changed.emit(self.settings_manager.settings)
            except Exception as e:
                print(f"Error emitting settings changed signal: {e}")
            
            # Show success message
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")
            
            self.accept()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Save Error", f"Failed to save settings: {str(e)}")
    
    def refresh_ollama_models(self):
        """Refresh the list of available Ollama models."""
        try:
            import requests
            import json
            
            # Get endpoint from the field
            try:
                endpoint = self.ollama_endpoint_edit.text().strip() or "http://localhost:11434"
            except:
                endpoint = "http://localhost:11434"
            
            # Try to fetch models from Ollama
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                if 'models' in data:
                    for model in data['models']:
                        if 'name' in model:
                            models.append(model['name'])
                
                # Clear and populate combo box
                self.ollama_model_combo.clear()
                if models:
                    self.ollama_model_combo.addItems(models)
                    self.refresh_models_button.setToolTip(f"Found {len(models)} models")
                else:
                    self.ollama_model_combo.addItem("llama2")
                    self.refresh_models_button.setToolTip("No models found, added default")
            else:
                # Add default model if can't connect
                self.ollama_model_combo.clear()
                self.ollama_model_combo.addItem("llama2")
                self.refresh_models_button.setToolTip(f"Connection failed: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            # Can't connect to Ollama - add default models
            self.ollama_model_combo.clear()
            default_models = ["llama2", "codellama", "mistral", "neural-chat"]
            self.ollama_model_combo.addItems(default_models)
            self.refresh_models_button.setToolTip(f"Ollama not available: {str(e)}")
            
        except Exception as e:
            print(f"Error refreshing Ollama models: {e}")
            self.ollama_model_combo.clear()
            self.ollama_model_combo.addItem("llama2")
            self.refresh_models_button.setToolTip(f"Error: {str(e)}")
    
    def test_apis(self):
        """Test API connections."""
        # This would be implemented to test API connectivity
        QMessageBox.information(self, "API Test", "API testing functionality would be implemented here.")
    
    def test_hotkey(self):
        """Test hotkey combination."""
        hotkey = self.hotkey_edit.text().strip()
        if hotkey:
            QMessageBox.information(self, "Hotkey Test", f"Testing hotkey: {hotkey}\n\nThis would register the hotkey temporarily for testing.")
    
    def browse_database_path(self):
        """Browse for database file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose Database Location",
            self.db_path_edit.text(),
            "SQLite Database (*.db);;All Files (*)"
        )
        
        if file_path:
            self.db_path_edit.setText(file_path)
            self.settings_manager.set('database_path', file_path)
    
    def export_history(self):
        """Export analysis history."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export History",
            "bsm_history_export.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Implementation would export database to JSON
            QMessageBox.information(self, "Export", f"History export functionality would save to:\n{file_path}")
    
    def clear_history(self):
        """Clear analysis history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all analysis history?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Implementation would clear database
            QMessageBox.information(self, "Clear History", "History clearing functionality would be implemented here.")