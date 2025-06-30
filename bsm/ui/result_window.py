import sys
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QLabel,
                             QSplitter, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
import json
from typing import Dict, Any, Optional

class MarkdownRenderer(QWebEngineView):
    """Custom markdown renderer using QWebEngineView."""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWebEngineView {
                background-color: #2b2b2b;
                border: none;
            }
        """)
    
    def render_markdown(self, markdown_text: str):
        """Render markdown text as HTML."""
        # Convert markdown to HTML with extensions
        html = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'codehilite'],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
        
        # Add CSS styling for better appearance
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #ffffff;
                    max-width: none;
                    margin: 0;
                    padding: 20px;
                    background-color: #2b2b2b;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #4CAF50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                }}
                
                h1 {{ font-size: 2em; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #555555; padding-bottom: 8px; }}
                h3 {{ font-size: 1.25em; }}
                
                p {{ margin-bottom: 16px; }}
                
                ul, ol {{
                    margin-bottom: 16px;
                    padding-left: 30px;
                }}
                
                li {{
                    margin-bottom: 4px;
                }}
                
                blockquote {{
                    border-left: 4px solid #4CAF50;
                    margin: 0;
                    padding-left: 16px;
                    color: #cccccc;
                    font-style: italic;
                    background-color: #333333;
                    padding: 12px 16px;
                    border-radius: 4px;
                }}
                
                code {{
                    background-color: #404040;
                    color: #ffeb3b;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                    font-size: 0.85em;
                }}
                
                pre {{
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                    margin-bottom: 16px;
                }}
                
                pre code {{
                    background-color: transparent;
                    padding: 0;
                    color: #f8f8f2;
                }}
                
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 16px;
                }}
                
                th, td {{
                    border: 1px solid #555555;
                    padding: 8px 12px;
                    text-align: left;
                }}
                
                th {{
                    background-color: #404040;
                    font-weight: 600;
                    color: #ffffff;
                }}
                
                .fact-check {{
                    background-color: #1b4d1b;
                    border-left: 4px solid #4CAF50;
                    color: #ffffff;
                    padding: 12px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                
                .counter-argument {{
                    background-color: #4d3d1b;
                    border-left: 4px solid #ffc107;
                    color: #ffffff;
                    padding: 12px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                
                .error {{
                    background-color: #4d1b1b;
                    border-left: 4px solid #f44336;
                    color: #ffffff;
                    padding: 12px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                
                .confidence-score {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: #ffffff;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.setHtml(styled_html)

class ResultWindow(QMainWindow):
    """Main result display window with markdown rendering."""
    
    closed = pyqtSignal()
    copy_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_analysis = None
        self.markdown_content = ""
        self.init_ui()
        self.setup_styling()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BSM - Analysis Results")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with title and controls
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border: none;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        # Title label
        self.title_label = QLabel("BSM Analysis Results")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Copy button
        self.copy_button = QPushButton("📋 Copy Results")
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.copy_button.clicked.connect(self.copy_results)
        header_layout.addWidget(self.copy_button)
        
        layout.addWidget(header_frame)
        
        # Main content area with markdown renderer
        self.markdown_renderer = MarkdownRenderer()
        layout.addWidget(self.markdown_renderer)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_styling(self):
        """Setup window styling with dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #2b2b2b;
                border: none;
            }
            
            QStatusBar {
                background-color: #333333;
                border-top: 1px solid #555555;
                color: #cccccc;
                font-size: 12px;
            }
        """)
        
        # Set window flags for better behavior
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
    
    def display_analysis(self, analysis_data: Dict[str, Any], original_text: str = ""):
        """Display analysis results."""
        self.current_analysis = analysis_data
        
        # Generate markdown content
        self.markdown_content = self.format_analysis_as_markdown(analysis_data, original_text)
        
        # Render in the markdown viewer
        self.markdown_renderer.render_markdown(self.markdown_content)
        
        # Update status
        provider = analysis_data.get('provider_used', 'Unknown')
        confidence = analysis_data.get('confidence_score', 0)
        self.statusBar().showMessage(f"Analysis by {provider} | Confidence: {confidence:.1%}")
        
        # Update title with attitude mode
        attitude = analysis_data.get('attitude_mode', 'balanced')
        self.title_label.setText(f"BSM Analysis Results ({attitude.title()} Mode)")
    
    def format_analysis_as_markdown(self, analysis_data: Dict[str, Any], original_text: str = "") -> str:
        """Format analysis data as markdown."""
        if 'error' in analysis_data:
            return f"""# Analysis Error

**Error:** {analysis_data['error']}

**Original Text:**
> {original_text[:500]}{'...' if len(original_text) > 500 else ''}
"""
        
        # Handle different response formats
        if 'analysis' in analysis_data and not isinstance(analysis_data.get('fact_check'), dict):
            # Simple text analysis format
            return f"""# BSM Analysis Results

## Original Text
> {original_text[:500]}{'...' if len(original_text) > 500 else ''}

## Analysis
{analysis_data.get('analysis', 'No analysis available')}

---
**Provider:** {analysis_data.get('provider_used', 'Unknown')}
**Confidence:** {analysis_data.get('confidence_score', 0):.1%}
"""
        
        # Structured JSON format
        markdown_parts = ["# BSM Analysis Results\n"]
        
        if original_text:
            markdown_parts.append(f"## Original Text\n> {original_text[:500]}{'...' if len(original_text) > 500 else ''}\n")
        
        # Summary
        if 'summary' in analysis_data:
            markdown_parts.append(f"## Summary\n{analysis_data['summary']}\n")
        
        # Fact Check
        if 'fact_check' in analysis_data:
            fact_check = analysis_data['fact_check']
            markdown_parts.append("## Fact Check\n")
            
            if 'verified_facts' in fact_check and fact_check['verified_facts']:
                markdown_parts.append("### ✅ Verified Facts\n")
                for fact in fact_check['verified_facts']:
                    markdown_parts.append(f"- {fact}\n")
                markdown_parts.append("\n")
            
            if 'questionable_claims' in fact_check and fact_check['questionable_claims']:
                markdown_parts.append("### ❓ Questionable Claims\n")
                for claim in fact_check['questionable_claims']:
                    markdown_parts.append(f"- {claim}\n")
                markdown_parts.append("\n")
            
            if 'unsupported_assertions' in fact_check and fact_check['unsupported_assertions']:
                markdown_parts.append("### ❌ Unsupported Assertions\n")
                for assertion in fact_check['unsupported_assertions']:
                    markdown_parts.append(f"- {assertion}\n")
                markdown_parts.append("\n")
        
        # Logical Analysis
        if 'logical_analysis' in analysis_data:
            logical = analysis_data['logical_analysis']
            markdown_parts.append("## Logical Analysis\n")
            
            if 'fallacies_identified' in logical and logical['fallacies_identified']:
                markdown_parts.append("### 🚨 Logical Fallacies\n")
                for fallacy in logical['fallacies_identified']:
                    markdown_parts.append(f"- {fallacy}\n")
                markdown_parts.append("\n")
            
            if 'argument_strengths' in logical and logical['argument_strengths']:
                markdown_parts.append("### 💪 Argument Strengths\n")
                for strength in logical['argument_strengths']:
                    markdown_parts.append(f"- {strength}\n")
                markdown_parts.append("\n")
            
            if 'argument_weaknesses' in logical and logical['argument_weaknesses']:
                markdown_parts.append("### ⚠️ Argument Weaknesses\n")
                for weakness in logical['argument_weaknesses']:
                    markdown_parts.append(f"- {weakness}\n")
                markdown_parts.append("\n")
        
        # Counter Arguments
        if 'counter_arguments' in analysis_data and analysis_data['counter_arguments']:
            markdown_parts.append("## Counter Arguments\n")
            for i, counter in enumerate(analysis_data['counter_arguments'], 1):
                markdown_parts.append(f"{i}. {counter}\n")
            markdown_parts.append("\n")
        
        # Alternative Perspectives
        if 'alternative_perspectives' in analysis_data and analysis_data['alternative_perspectives']:
            markdown_parts.append("## Alternative Perspectives\n")
            for perspective in analysis_data['alternative_perspectives']:
                markdown_parts.append(f"- {perspective}\n")
            markdown_parts.append("\n")
        
        # Sources Needed
        if 'sources_needed' in analysis_data and analysis_data['sources_needed']:
            markdown_parts.append("## Sources Needed for Verification\n")
            for source in analysis_data['sources_needed']:
                markdown_parts.append(f"- {source}\n")
            markdown_parts.append("\n")
        
        # Conclusion
        if 'conclusion' in analysis_data:
            markdown_parts.append(f"## Conclusion\n{analysis_data['conclusion']}\n")
        
        # Footer with metadata
        confidence = analysis_data.get('confidence_score', 0)
        provider = analysis_data.get('provider_used', 'Unknown')
        
        markdown_parts.append("---\n")
        markdown_parts.append(f"**Provider:** {provider} | ")
        markdown_parts.append(f"**Confidence:** <span class='confidence-score'>{confidence:.1%}</span>")
        
        if analysis_data.get('fallback_used'):
            markdown_parts.append(" | **Fallback Used**")
        
        return "".join(markdown_parts)
    
    def copy_results(self):
        """Copy analysis results to clipboard."""
        if self.markdown_content:
            self.copy_requested.emit(self.markdown_content)
            self.statusBar().showMessage("Results copied to clipboard!", 3000)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.closed.emit()
        event.accept()
    
    def save_position(self) -> Dict[str, int]:
        """Save current window position and size."""
        geometry = self.geometry()
        return {
            'x': geometry.x(),
            'y': geometry.y(),
            'width': geometry.width(),
            'height': geometry.height()
        }
    
    def restore_position(self, position: Dict[str, int]):
        """Restore window position and size."""
        try:
            self.setGeometry(
                position.get('x', 100),
                position.get('y', 100),
                position.get('width', 900),
                position.get('height', 700)
            )
        except Exception as e:
            print(f"Error restoring window position: {e}")
            # Use defaults
            self.setGeometry(100, 100, 900, 700)