"""
Improved Hotkey Manager with enhanced reliability and features.

This module provides a more robust hotkey management system with:
- Multiple hotkey support
- Better platform-specific handling
- Validation and fallback mechanisms
- Attitude mode switching support
"""

import sys
import logging
from typing import Dict, Callable, Optional, Set, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import threading
import time

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)


class HotkeyBackend(Enum):
    """Available hotkey backend implementations."""
    PYNPUT = "pynput"
    KEYBOARD = "keyboard"
    NATIVE = "native"


@dataclass
class HotkeyRegistration:
    """Represents a registered hotkey."""
    id: str
    combination: str
    callback: Callable
    description: str
    backend: HotkeyBackend
    active: bool = True


class HotkeyValidator:
    """Validates hotkey combinations."""
    
    # Reserved system combinations by platform
    RESERVED_COMBINATIONS = {
        'darwin': {
            'cmd+q', 'cmd+w', 'cmd+tab', 'cmd+space', 'cmd+h', 'cmd+m',
            'cmd+shift+3', 'cmd+shift+4', 'cmd+shift+5'
        },
        'win32': {
            'alt+f4', 'alt+tab', 'ctrl+alt+del', 'win+l', 'win+d',
            'ctrl+shift+esc', 'win+tab'
        },
        'linux': {
            'alt+f4', 'alt+tab', 'ctrl+alt+del', 'ctrl+alt+f1',
            'ctrl+alt+f2', 'ctrl+alt+f3', 'ctrl+alt+f4'
        }
    }
    
    @classmethod
    def is_valid_combination(cls, combination: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a hotkey combination is valid.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        combination = combination.lower().strip()
        
        # Check for empty combination
        if not combination:
            return False, "Hotkey combination cannot be empty"
        
        # Parse combination
        parts = combination.split('+')
        if len(parts) < 2:
            return False, "Hotkey must include at least one modifier and one key"
        
        # Check for modifiers
        modifiers = {'ctrl', 'shift', 'alt', 'cmd', 'win', 'meta', 'super'}
        has_modifier = any(part in modifiers for part in parts[:-1])
        
        if not has_modifier:
            return False, "Hotkey must include at least one modifier key"
        
        # Check for reserved combinations
        platform = sys.platform
        reserved = cls.RESERVED_COMBINATIONS.get(platform, set())
        
        if combination in reserved:
            return False, f"This combination is reserved by the system"
        
        return True, None


class HotkeyCallbackHandler(QObject):
    """Qt-safe callback handler for hotkeys."""
    
    triggered = pyqtSignal(str)  # hotkey_id
    
    def __init__(self):
        super().__init__()
        self.callbacks: Dict[str, Callable] = {}
        self.triggered.connect(self._execute_callback)
    
    def register_callback(self, hotkey_id: str, callback: Callable):
        """Register a callback for a hotkey ID."""
        self.callbacks[hotkey_id] = callback
    
    def unregister_callback(self, hotkey_id: str):
        """Unregister a callback."""
        self.callbacks.pop(hotkey_id, None)
    
    def trigger(self, hotkey_id: str):
        """Trigger a hotkey callback (thread-safe)."""
        self.triggered.emit(hotkey_id)
    
    def _execute_callback(self, hotkey_id: str):
        """Execute callback on Qt main thread."""
        callback = self.callbacks.get(hotkey_id)
        if callback:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in hotkey callback {hotkey_id}: {e}")


class BaseHotkeyBackend(ABC):
    """Abstract base class for hotkey backends."""
    
    def __init__(self, callback_handler: HotkeyCallbackHandler):
        self.callback_handler = callback_handler
        self._active = False
    
    @abstractmethod
    def register(self, registration: HotkeyRegistration) -> bool:
        """Register a hotkey. Returns True on success."""
        pass
    
    @abstractmethod
    def unregister(self, hotkey_id: str) -> bool:
        """Unregister a hotkey. Returns True on success."""
        pass
    
    @abstractmethod
    def start(self):
        """Start the backend listener."""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the backend listener."""
        pass
    
    @property
    def is_active(self) -> bool:
        """Check if backend is active."""
        return self._active


class PynputBackend(BaseHotkeyBackend):
    """Pynput-based hotkey backend."""
    
    def __init__(self, callback_handler: HotkeyCallbackHandler):
        super().__init__(callback_handler)
        self.listener = None
        self.registrations: Dict[str, HotkeyRegistration] = {}
        self.current_keys: Set = set()
        self._lock = threading.Lock()
    
    def register(self, registration: HotkeyRegistration) -> bool:
        """Register a hotkey with pynput."""
        try:
            from pynput import keyboard
            
            # Parse hotkey combination
            keys = self._parse_combination(registration.combination)
            if not keys:
                return False
            
            with self._lock:
                self.registrations[registration.id] = registration
            
            # Restart listener if active
            if self._active:
                self.stop()
                self.start()
            
            return True
            
        except ImportError:
            logger.error("pynput not available")
            return False
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
            return False
    
    def unregister(self, hotkey_id: str) -> bool:
        """Unregister a hotkey."""
        with self._lock:
            if hotkey_id in self.registrations:
                del self.registrations[hotkey_id]
                return True
        return False
    
    def start(self):
        """Start the pynput listener."""
        if self._active or not self.registrations:
            return
        
        try:
            from pynput import keyboard
            
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self._active = True
            logger.info("Pynput backend started")
            
        except Exception as e:
            logger.error(f"Failed to start pynput backend: {e}")
            self._active = False
    
    def stop(self):
        """Stop the pynput listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self._active = False
        self.current_keys.clear()
        logger.info("Pynput backend stopped")
    
    def _parse_combination(self, combination: str) -> Set:
        """Parse hotkey combination string into key set."""
        from pynput import keyboard
        
        parts = combination.lower().split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            
            # Modifiers
            if part in ('ctrl', 'control'):
                keys.add(keyboard.Key.ctrl_l)
                keys.add(keyboard.Key.ctrl_r)
            elif part == 'shift':
                keys.add(keyboard.Key.shift_l)
                keys.add(keyboard.Key.shift_r)
            elif part == 'alt':
                keys.add(keyboard.Key.alt_l)
                keys.add(keyboard.Key.alt_r)
            elif part in ('cmd', 'command', 'meta', 'win', 'super'):
                if sys.platform == 'darwin':
                    keys.add(keyboard.Key.cmd)
                else:
                    keys.add(keyboard.Key.cmd_l)
                    keys.add(keyboard.Key.cmd_r)
            # Regular keys
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            # Function keys
            elif part.startswith('f') and part[1:].isdigit():
                try:
                    keys.add(getattr(keyboard.Key, part))
                except AttributeError:
                    pass
        
        return keys
    
    def _normalize_key(self, key):
        """Normalize key for comparison."""
        from pynput import keyboard
        
        # Handle both Key and KeyCode types
        if hasattr(key, 'char') and key.char:
            return keyboard.KeyCode.from_char(key.char.lower())
        elif hasattr(key, 'vk'):
            return key
        elif isinstance(key, keyboard.Key):
            return key
        return key
    
    def _on_press(self, key):
        """Handle key press event."""
        normalized = self._normalize_key(key)
        self.current_keys.add(normalized)
        
        # Check all registered combinations
        with self._lock:
            for reg_id, registration in self.registrations.items():
                if not registration.active:
                    continue
                
                required_keys = self._parse_combination(registration.combination)
                
                # Check if all required keys are pressed
                if all(any(self._keys_match(k, pressed) for pressed in self.current_keys) 
                       for k in required_keys):
                    logger.debug(f"Hotkey triggered: {registration.combination}")
                    self.callback_handler.trigger(reg_id)
    
    def _on_release(self, key):
        """Handle key release event."""
        normalized = self._normalize_key(key)
        self.current_keys.discard(normalized)
        
        # Also remove variants
        from pynput import keyboard
        if isinstance(normalized, keyboard.Key):
            # Remove both left and right variants
            if normalized == keyboard.Key.ctrl_l:
                self.current_keys.discard(keyboard.Key.ctrl_r)
            elif normalized == keyboard.Key.ctrl_r:
                self.current_keys.discard(keyboard.Key.ctrl_l)
            # Similar for other modifiers
    
    def _keys_match(self, key1, key2) -> bool:
        """Check if two keys match (handling variants)."""
        from pynput import keyboard
        
        # Direct match
        if key1 == key2:
            return True
        
        # Check modifier variants
        modifier_groups = [
            (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r),
            (keyboard.Key.shift_l, keyboard.Key.shift_r),
            (keyboard.Key.alt_l, keyboard.Key.alt_r),
        ]
        
        for group in modifier_groups:
            if key1 in group and key2 in group:
                return True
        
        return False


class ImprovedHotkeyManager:
    """
    Enhanced hotkey manager with multiple backend support and validation.
    """
    
    def __init__(self):
        self.callback_handler = HotkeyCallbackHandler()
        self.registrations: Dict[str, HotkeyRegistration] = {}
        self.backends: Dict[HotkeyBackend, BaseHotkeyBackend] = {}
        self.primary_backend: Optional[HotkeyBackend] = None
        
        # Initialize available backends
        self._init_backends()
    
    def _init_backends(self):
        """Initialize available hotkey backends."""
        # Try pynput first (most cross-platform)
        try:
            self.backends[HotkeyBackend.PYNPUT] = PynputBackend(self.callback_handler)
            self.primary_backend = HotkeyBackend.PYNPUT
            logger.info("Initialized pynput backend")
        except Exception as e:
            logger.warning(f"Failed to initialize pynput backend: {e}")
        
        # Add other backends as needed (keyboard, native, etc.)
    
    def register_hotkey(
        self,
        hotkey_id: str,
        combination: str,
        callback: Callable,
        description: str = "",
        validate: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a hotkey with validation and fallback support.
        
        Returns:
            Tuple of (success, error_message)
        """
        # Validate combination
        if validate:
            is_valid, error = HotkeyValidator.is_valid_combination(combination)
            if not is_valid:
                return False, error
        
        # Check for duplicate ID
        if hotkey_id in self.registrations:
            return False, f"Hotkey ID '{hotkey_id}' already registered"
        
        # Create registration
        registration = HotkeyRegistration(
            id=hotkey_id,
            combination=combination,
            callback=callback,
            description=description,
            backend=self.primary_backend
        )
        
        # Register callback handler
        self.callback_handler.register_callback(hotkey_id, callback)
        
        # Try to register with backend
        backend = self.backends.get(self.primary_backend)
        if backend and backend.register(registration):
            self.registrations[hotkey_id] = registration
            logger.info(f"Registered hotkey '{combination}' with ID '{hotkey_id}'")
            return True, None
        
        # Fallback to other backends
        for backend_type, backend in self.backends.items():
            if backend_type != self.primary_backend and backend.register(registration):
                registration.backend = backend_type
                self.registrations[hotkey_id] = registration
                logger.info(f"Registered hotkey '{combination}' with fallback backend {backend_type}")
                return True, None
        
        # Registration failed
        self.callback_handler.unregister_callback(hotkey_id)
        return False, "Failed to register hotkey with any backend"
    
    def unregister_hotkey(self, hotkey_id: str) -> bool:
        """Unregister a hotkey."""
        if hotkey_id not in self.registrations:
            return False
        
        registration = self.registrations[hotkey_id]
        backend = self.backends.get(registration.backend)
        
        if backend:
            backend.unregister(hotkey_id)
        
        self.callback_handler.unregister_callback(hotkey_id)
        del self.registrations[hotkey_id]
        
        logger.info(f"Unregistered hotkey with ID '{hotkey_id}'")
        return True
    
    def enable_hotkey(self, hotkey_id: str) -> bool:
        """Enable a disabled hotkey."""
        if hotkey_id in self.registrations:
            self.registrations[hotkey_id].active = True
            return True
        return False
    
    def disable_hotkey(self, hotkey_id: str) -> bool:
        """Temporarily disable a hotkey."""
        if hotkey_id in self.registrations:
            self.registrations[hotkey_id].active = False
            return True
        return False
    
    def update_hotkey(self, hotkey_id: str, new_combination: str) -> Tuple[bool, Optional[str]]:
        """Update an existing hotkey combination."""
        if hotkey_id not in self.registrations:
            return False, "Hotkey ID not found"
        
        # Validate new combination
        is_valid, error = HotkeyValidator.is_valid_combination(new_combination)
        if not is_valid:
            return False, error
        
        # Get current registration
        registration = self.registrations[hotkey_id]
        
        # Unregister old combination
        self.unregister_hotkey(hotkey_id)
        
        # Register with new combination
        return self.register_hotkey(
            hotkey_id,
            new_combination,
            registration.callback,
            registration.description
        )
    
    def start(self):
        """Start all active backends."""
        for backend in self.backends.values():
            backend.start()
        logger.info("Hotkey manager started")
    
    def stop(self):
        """Stop all backends."""
        for backend in self.backends.values():
            backend.stop()
        logger.info("Hotkey manager stopped")
    
    def get_registered_hotkeys(self) -> Dict[str, Dict[str, str]]:
        """Get information about all registered hotkeys."""
        return {
            hotkey_id: {
                'combination': reg.combination,
                'description': reg.description,
                'active': reg.active,
                'backend': reg.backend.value
            }
            for hotkey_id, reg in self.registrations.items()
        }
    
    def test_hotkey(self, combination: str) -> Tuple[bool, Optional[str]]:
        """Test if a hotkey combination can be registered."""
        # First validate
        is_valid, error = HotkeyValidator.is_valid_combination(combination)
        if not is_valid:
            return False, error
        
        # Try a temporary registration
        test_id = f"test_{time.time()}"
        success, error = self.register_hotkey(
            test_id,
            combination,
            lambda: None,
            "Test hotkey"
        )
        
        # Clean up
        if success:
            self.unregister_hotkey(test_id)
        
        return success, error


# Convenience function for backward compatibility
def create_improved_hotkey_manager() -> ImprovedHotkeyManager:
    """Create an improved hotkey manager instance."""
    return ImprovedHotkeyManager()
