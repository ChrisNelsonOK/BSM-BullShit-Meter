"""
macOS-specific hotkey manager using AppKit event monitoring.
This avoids the threading issues with pynput on macOS.
"""

import sys
from typing import Callable, Optional

if sys.platform == 'darwin':
    try:
        import Cocoa
        from PyQt6.QtCore import QObject, pyqtSignal
        MACOS_AVAILABLE = True
    except ImportError:
        MACOS_AVAILABLE = False
else:
    MACOS_AVAILABLE = False

class MacOSHotkeyManager(QObject):
    """macOS-specific hotkey manager using NSEvent monitoring."""
    
    def __init__(self):
        super().__init__()
        self.monitor = None
        self.callback = None
        self.hotkey_combination = None
        self.current_keys = set()
        
    def parse_hotkey_string(self, hotkey_string: str) -> dict:
        """Parse hotkey string into macOS modifier flags and key code."""
        if not MACOS_AVAILABLE:
            return {}
            
        parts = hotkey_string.lower().split('+')
        modifiers = 0
        key_char = None
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                modifiers |= Cocoa.NSEventModifierFlagControl
            elif part == 'shift':
                modifiers |= Cocoa.NSEventModifierFlagShift
            elif part == 'alt' or part == 'option':
                modifiers |= Cocoa.NSEventModifierFlagOption
            elif part == 'cmd' or part == 'meta':
                modifiers |= Cocoa.NSEventModifierFlagCommand
            elif len(part) == 1:
                key_char = part
        
        return {'modifiers': modifiers, 'key': key_char}
    
    def register_hotkey(self, hotkey_string: str, callback: Callable):
        """Register a global hotkey using NSEvent monitoring."""
        if not MACOS_AVAILABLE:
            print("macOS hotkey manager not available (missing pyobjc)")
            return
            
        self.hotkey_combination = self.parse_hotkey_string(hotkey_string)
        self.callback = callback
        
        if self.monitor:
            self.unregister_hotkey()
        
        try:
            # Create an event monitor for key down events
            self.monitor = Cocoa.NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                Cocoa.NSEventMaskKeyDown,
                self._handle_event
            )
            print(f"macOS hotkey {hotkey_string} registered successfully")
            print("Note: You may need to grant accessibility permissions in System Preferences > Privacy & Security > Accessibility")
        except Exception as e:
            print(f"Failed to register macOS hotkey: {e}")
            print("This may be due to missing accessibility permissions.")
    
    def unregister_hotkey(self):
        """Unregister the current hotkey."""
        if self.monitor:
            try:
                Cocoa.NSEvent.removeMonitor_(self.monitor)
            except:
                pass
            self.monitor = None
        self.callback = None
        self.hotkey_combination = None
    
    def _handle_event(self, event):
        """Handle NSEvent for hotkey detection."""
        if not self.hotkey_combination or not self.callback:
            return
        
        try:
            # Get event modifiers and key
            modifiers = event.modifierFlags()
            key_char = event.charactersIgnoringModifiers()
            
            # Check if modifiers match
            expected_modifiers = self.hotkey_combination.get('modifiers', 0)
            expected_key = self.hotkey_combination.get('key', '')
            
            # Filter out irrelevant modifier flags
            relevant_modifiers = modifiers & (
                Cocoa.NSEventModifierFlagControl |
                Cocoa.NSEventModifierFlagShift |
                Cocoa.NSEventModifierFlagOption |
                Cocoa.NSEventModifierFlagCommand
            )
            
            if (relevant_modifiers == expected_modifiers and 
                key_char and key_char.lower() == expected_key.lower()):
                # Emit signal to execute on main thread
                try:
                    self.callback()
                except Exception as e:
                    print(f"Error in hotkey callback: {e}")
        except Exception as e:
            print(f"Error handling hotkey event: {e}")

def create_macos_hotkey_manager():
    """Create macOS-specific hotkey manager if available."""
    if MACOS_AVAILABLE and sys.platform == 'darwin':
        return MacOSHotkeyManager()
    else:
        return None