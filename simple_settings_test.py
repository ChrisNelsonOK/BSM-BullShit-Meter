#!/usr/bin/env python3
"""
Simple settings test focused on the save crash
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from bsm.core.settings import SettingsManager
from bsm.ui.settings_window import SettingsWindow

def simple_test():
    """Simple test of settings window."""
    app = QApplication(sys.argv)
    
    print("Creating settings manager...")
    settings = SettingsManager()
    
    print("Creating settings window...")
    window = SettingsWindow(settings)
    
    print("Setting test values...")
    window.openai_key_edit.setText("sk-test123")
    window.claude_key_edit.setText("sk-ant-test123")
    
    print("Attempting save...")
    try:
        window.save_settings()
        print("✓ Save successful!")
    except Exception as e:
        print(f"✗ Save failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("Test completed")

if __name__ == "__main__":
    simple_test()