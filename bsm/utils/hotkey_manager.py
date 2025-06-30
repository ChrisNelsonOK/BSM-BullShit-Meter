import sys
from typing import Callable, Optional
from pynput import keyboard
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class HotkeyCallbackHandler(QObject):
    """Qt object to handle hotkey callbacks on main thread."""
    
    callback_triggered = pyqtSignal()
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.callback_triggered.connect(self._execute_callback)
    
    def _execute_callback(self):
        """Execute callback safely on main thread."""
        try:
            if self.callback:
                self.callback()
        except Exception as e:
            print(f"Error in hotkey callback: {e}")

class HotkeyManager:
    """Cross-platform global hotkey manager."""
    
    def __init__(self):
        self.listener = None
        self.hotkey_combination = None
        self.callback = None
        self.current_keys = set()
        self._running = False
        self._callback_handler = None
    
    def parse_hotkey_string(self, hotkey_string: str) -> set:
        """Parse hotkey string like 'ctrl+shift+b' into key set."""
        parts = hotkey_string.lower().split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl_l)
                keys.add(keyboard.Key.ctrl_r)
            elif part == 'shift':
                keys.add(keyboard.Key.shift_l)
                keys.add(keyboard.Key.shift_r)
            elif part == 'alt':
                keys.add(keyboard.Key.alt_l)
                keys.add(keyboard.Key.alt_r)
            elif part == 'cmd' or part == 'meta':
                if sys.platform == 'darwin':
                    keys.add(keyboard.Key.cmd)
                else:
                    keys.add(keyboard.Key.alt_l)
            elif len(part) == 1:
                try:
                    keys.add(keyboard.KeyCode.from_char(part))
                except:
                    # Handle special characters
                    if part == ' ':
                        keys.add(keyboard.Key.space)
                    elif part == '\t':
                        keys.add(keyboard.Key.tab)
        
        return keys
    
    def register_hotkey(self, hotkey_string: str, callback: Callable):
        """Register a global hotkey."""
        self.hotkey_combination = self.parse_hotkey_string(hotkey_string)
        self.callback = callback
        
        # Create Qt callback handler for thread-safe execution
        self._callback_handler = HotkeyCallbackHandler(callback)
        
        if self.listener:
            self.listener.stop()
        
        self._running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def unregister_hotkey(self):
        """Unregister the current hotkey."""
        self._running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.hotkey_combination = None
        self.callback = None
        self._callback_handler = None
        self.current_keys.clear()
    
    def _normalize_key(self, key):
        """Normalize key for comparison."""
        try:
            # Handle special keys
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return keyboard.Key.ctrl_l
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                return keyboard.Key.shift_l
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return keyboard.Key.alt_l
            else:
                return key
        except AttributeError:
            return key
    
    def _on_press(self, key):
        """Handle key press events."""
        if not self._running or not self.hotkey_combination:
            return
        
        try:
            normalized_key = self._normalize_key(key)
            self.current_keys.add(normalized_key)
            
            # Check if current keys match hotkey combination
            if self._keys_match():
                if self._callback_handler:
                    # Emit signal to execute callback on main thread
                    self._callback_handler.callback_triggered.emit()
        except Exception as e:
            print(f"Error in hotkey press handler: {e}")
    
    def _on_release(self, key):
        """Handle key release events."""
        if not self._running:
            return
        
        normalized_key = self._normalize_key(key)
        self.current_keys.discard(normalized_key)
    
    def _keys_match(self) -> bool:
        """Check if current keys match the hotkey combination."""
        if not self.hotkey_combination:
            return False
        
        # Normalize both sets for comparison
        current_normalized = set()
        hotkey_normalized = set()
        
        for key in self.current_keys:
            current_normalized.add(self._normalize_key(key))
        
        for key in self.hotkey_combination:
            hotkey_normalized.add(self._normalize_key(key))
        
        # Check if all required keys are pressed
        required_modifiers = {k for k in hotkey_normalized if hasattr(k, 'name')}
        required_chars = hotkey_normalized - required_modifiers
        
        current_modifiers = {k for k in current_normalized if hasattr(k, 'name')}
        current_chars = current_normalized - current_modifiers
        
        # All required modifiers must be present
        modifiers_match = required_modifiers.issubset(current_modifiers)
        
        # At least one required character must be present
        chars_match = len(required_chars) == 0 or len(required_chars.intersection(current_chars)) > 0
        
        return modifiers_match and chars_match

class MacOSHotkeyManager(HotkeyManager):
    """macOS-specific hotkey manager with better key handling."""
    
    def parse_hotkey_string(self, hotkey_string: str) -> set:
        """Parse hotkey string with macOS-specific mappings."""
        parts = hotkey_string.lower().split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl)
            elif part == 'shift':
                keys.add(keyboard.Key.shift)
            elif part == 'alt' or part == 'option':
                keys.add(keyboard.Key.alt)
            elif part == 'cmd' or part == 'meta':
                keys.add(keyboard.Key.cmd)
            elif len(part) == 1:
                try:
                    keys.add(keyboard.KeyCode.from_char(part))
                except:
                    if part == ' ':
                        keys.add(keyboard.Key.space)
                    elif part == '\t':
                        keys.add(keyboard.Key.tab)
        
        return keys

def create_hotkey_manager() -> HotkeyManager:
    """Create appropriate hotkey manager for the current platform."""
    if sys.platform == 'darwin':
        # Try to use macOS-specific implementation first
        try:
            from .macos_hotkey_manager import create_macos_hotkey_manager
            macos_manager = create_macos_hotkey_manager()
            if macos_manager:
                return macos_manager
        except ImportError:
            print("macOS hotkey manager not available, falling back to standard implementation")
        
        # Fallback to regular macOS implementation
        return MacOSHotkeyManager()
    else:
        return HotkeyManager()