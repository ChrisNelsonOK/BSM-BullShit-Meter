"""
BSM Analysis Results Window

A beautiful popup window to display AI analysis results with markdown formatting
and copy/paste functionality.
"""

import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QApplication, QMessageBox,
                            QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import logging

logger = logging.getLogger(__name__)


class ResultsWindow(QDialog):
    """Beautiful results window for displaying AI analysis results."""
    
    def __init__(self, analysis_result, parent=None):
        super().__init__(parent)
        self.analysis_result = analysis_result
        self.markdown_content = ""
        self.init_ui()
        self.generate_markdown()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🔍 BSM Analysis Results")
        self.setModal(True)
        self.resize(800, 600)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Results display area
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setFont(QFont("SF Pro Display", 12))
        layout.addWidget(self.results_display)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Copy button
        copy_btn = QPushButton("📋 Copy Markdown")
        copy_btn.setFont(QFont("SF Pro Display", 11, QFont.Weight.Medium))
        copy_btn.clicked.connect(self.copy_markdown)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        
        # Copy Plain Text button
        copy_plain_btn = QPushButton("📄 Copy Plain Text")
        copy_plain_btn.setFont(QFont("SF Pro Display", 11, QFont.Weight.Medium))
        copy_plain_btn.clicked.connect(self.copy_plain_text)
        copy_plain_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #28A745;
            }
            QPushButton:pressed {
                background-color: #1E7E34;
            }
        """)
        
        # Close button
        close_btn = QPushButton("✕ Close")
        close_btn.setFont(QFont("SF Pro Display", 11, QFont.Weight.Medium))
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #8E8E93;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #6D6D70;
            }
            QPushButton:pressed {
                background-color: #48484A;
            }
        """)
        
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(copy_plain_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Window styling
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 16px;
                font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                line-height: 1.6;
            }
            QLabel {
                color: #1D1D1F;
            }
        """)
        
    def create_header(self):
        """Create the header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        # Title
        title = QLabel("🔍 BSM Analysis Results")
        title.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1D1D1F; margin-bottom: 4px;")
        
        # Subtitle with provider info
        provider = self.analysis_result.get('provider', 'AI Provider')
        attitude = self.analysis_result.get('attitude_mode', 'balanced').title()
        subtitle = QLabel(f"🤖 Analyzed by {provider} • 🎯 {attitude} Mode")
        subtitle.setFont(QFont("SF Pro Display", 13))
        subtitle.setStyleSheet("color: #8E8E93; margin-bottom: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        
        return header_frame
        
    def generate_markdown(self):
        """Generate markdown content from analysis results."""
        result = self.analysis_result
        
        # Start with header
        markdown = "# 🔍 BSM Analysis Results\n\n"
        
        # Metadata
        provider = result.get('provider', 'AI Provider')
        attitude = result.get('attitude_mode', 'balanced').title()
        markdown += f"**🤖 Provider:** {provider}  \n"
        markdown += f"**🎯 Analysis Mode:** {attitude}  \n"
        
        if 'confidence' in result:
            markdown += f"**📊 Confidence:** {result['confidence']}%  \n"
            
        markdown += "\n---\n\n"
        
        # Fact Check Section
        if 'fact_check' in result and result['fact_check']:
            markdown += "## 📊 Fact Check\n\n"
            markdown += f"{result['fact_check']}\n\n"
        
        # Counter-Argument Section
        if 'counter_argument' in result and result['counter_argument']:
            markdown += "## 🎭 Counter-Argument\n\n"
            markdown += f"{result['counter_argument']}\n\n"
        
        # Sources Section
        if 'sources' in result and result['sources']:
            markdown += "## 📚 Sources\n\n"
            for i, source in enumerate(result['sources'], 1):
                markdown += f"{i}. {source}\n"
            markdown += "\n"
        
        # Additional Analysis
        if 'analysis' in result and result['analysis']:
            markdown += "## 🔬 Additional Analysis\n\n"
            markdown += f"{result['analysis']}\n\n"
        
        # Summary
        if 'summary' in result and result['summary']:
            markdown += "## 📝 Summary\n\n"
            markdown += f"{result['summary']}\n\n"
        
        # Footer
        markdown += "---\n\n"
        markdown += "*Generated by BSM (BullShit Meter) - AI-Enhanced Fact Checking*\n"
        
        self.markdown_content = markdown
        
        # Display in the text area with basic formatting
        self.display_formatted_results()
        
    def display_formatted_results(self):
        """Display formatted results in the text area."""
        # Convert markdown to HTML for better display
        html_content = self.markdown_to_html(self.markdown_content)
        self.results_display.setHtml(html_content)
        
    def markdown_to_html(self, markdown_text):
        """Convert basic markdown to HTML for display."""
        html = markdown_text
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n\n', '</h1>\n\n')
        html = html.replace('## ', '<h2>').replace('\n\n', '</h2>\n\n')
        
        # Bold text
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Line breaks
        html = html.replace('  \n', '<br>')
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        # Horizontal rules
        html = html.replace('---', '<hr>')
        
        # Wrap in paragraphs
        html = f'<p>{html}</p>'
        
        # Fix header tags
        html = html.replace('<h1></h1>', '<h1>')
        html = html.replace('<h2></h2>', '<h2>')
        html = html.replace('</p><p><h1>', '<h1>')
        html = html.replace('</p><p><h2>', '<h2>')
        html = html.replace('</p><p><hr>', '<hr>')
        
        # Style the HTML
        styled_html = f"""
        <style>
            body {{ 
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: #1D1D1F;
                margin: 0;
                padding: 0;
            }}
            h1 {{ 
                color: #007AFF;
                font-size: 24px;
                font-weight: 700;
                margin: 20px 0 16px 0;
                border-bottom: 2px solid #007AFF;
                padding-bottom: 8px;
            }}
            h2 {{ 
                color: #34C759;
                font-size: 18px;
                font-weight: 600;
                margin: 24px 0 12px 0;
            }}
            p {{ 
                margin: 12px 0;
                font-size: 14px;
            }}
            strong {{ 
                font-weight: 600;
                color: #1D1D1F;
            }}
            hr {{ 
                border: none;
                height: 1px;
                background-color: #E5E5EA;
                margin: 24px 0;
            }}
        </style>
        <body>{html}</body>
        """
        
        return styled_html
        
    def copy_markdown(self):
        """Copy markdown content to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.markdown_content)
        
        # Show confirmation
        QMessageBox.information(self, "Copied!", 
                              "📋 Markdown content copied to clipboard!\n\n"
                              "You can now paste it into any markdown editor.")
        
    def copy_plain_text(self):
        """Copy plain text content to clipboard."""
        # Convert markdown to plain text
        plain_text = self.markdown_content
        
        # Remove markdown formatting
        import re
        plain_text = re.sub(r'#+\s*', '', plain_text)  # Remove headers
        plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', plain_text)  # Remove bold
        plain_text = re.sub(r'\*(.*?)\*', r'\1', plain_text)  # Remove italic
        plain_text = plain_text.replace('---', '=' * 50)  # Replace hr with equals
        plain_text = re.sub(r'\n\n+', '\n\n', plain_text)  # Clean up extra newlines
        
        clipboard = QApplication.clipboard()
        clipboard.setText(plain_text)
        
        # Show confirmation
        QMessageBox.information(self, "Copied!", 
                              "📄 Plain text content copied to clipboard!\n\n"
                              "You can now paste it anywhere.")


if __name__ == "__main__":
    # Test the results window
    app = QApplication(sys.argv)
    
    # Sample analysis result
    sample_result = {
        'provider': 'OpenAI GPT-4',
        'attitude_mode': 'balanced',
        'confidence': 85,
        'fact_check': 'The claim appears to be partially accurate based on available evidence. However, some aspects require further verification.',
        'counter_argument': 'While the main premise has merit, alternative perspectives suggest that the situation may be more nuanced than initially presented.',
        'sources': [
            'https://example.com/source1',
            'https://example.com/source2',
            'Academic Journal Reference'
        ],
        'summary': 'The analysis reveals a complex situation that requires careful consideration of multiple viewpoints.'
    }
    
    window = ResultsWindow(sample_result)
    window.show()
    
    sys.exit(app.exec())
