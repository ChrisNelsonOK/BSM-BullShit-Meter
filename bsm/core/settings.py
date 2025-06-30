import os
import json
import yaml
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64

class SettingsManager:
    """Manages application settings with encryption for sensitive data."""
    
    DEFAULT_SETTINGS = {
        'api_keys': {
            'openai': '',
            'claude': ''
        },
        'llm_provider': 'openai',  # 'openai', 'claude', 'ollama'
        'ollama_endpoint': 'http://localhost:11434',
        'ollama_model': 'llama2',
        'attitude_mode': 'balanced',  # 'argumentative', 'balanced', 'helpful'
        'global_hotkey': 'ctrl+shift+b',
        'database_path': '',
        'window_position': {'x': 100, 'y': 100, 'width': 800, 'height': 600},
        'auto_save_results': True,
        'show_confidence_score': True,
        'enable_screenshot_ocr': True
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            self.config_dir = os.path.join(os.path.expanduser('~'), '.bsm')
        else:
            self.config_dir = config_dir
            
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, 'settings.yaml')
        self.key_file = os.path.join(self.config_dir, '.key')
        
        self._encryption_key = self._get_or_create_key()
        self._cipher = Fernet(self._encryption_key)
        
        self.settings = self._load_settings()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for sensitive data."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return base64.urlsafe_b64decode(f.read())
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(base64.urlsafe_b64encode(key))
            return key
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value."""
        if not value:
            return value
        try:
            return self._cipher.encrypt(value.encode()).decode()
        except Exception:
            return value
    
    def _decrypt_value(self, value: str) -> str:
        """Decrypt a sensitive value."""
        if not value:
            return value
        try:
            return self._cipher.decrypt(value.encode()).decode()
        except Exception:
            return value
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = yaml.safe_load(f) or {}
                
                # Merge with defaults
                merged_settings = self.DEFAULT_SETTINGS.copy()
                merged_settings.update(settings)
                settings = merged_settings
                
                # Decrypt API keys
                if 'api_keys' in settings:
                    for key in settings['api_keys']:
                        settings['api_keys'][key] = self._decrypt_value(settings['api_keys'][key])
                
                return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save settings to file with encryption for sensitive data."""
        settings_to_save = self.settings.copy()
        
        # Encrypt API keys before saving
        if 'api_keys' in settings_to_save:
            encrypted_keys = {}
            for key, value in settings_to_save['api_keys'].items():
                encrypted_keys[key] = self._encrypt_value(value)
            settings_to_save['api_keys'] = encrypted_keys
        
        try:
            with open(self.settings_file, 'w') as f:
                yaml.dump(settings_to_save, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set a setting value."""
        keys = key.split('.')
        target = self.settings
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
    
    def get_database_path(self) -> str:
        """Get the database path, creating default if not set."""
        db_path = self.get('database_path')
        if not db_path:
            db_path = os.path.join(self.config_dir, 'bsm_history.db')
            self.set('database_path', db_path)
            self.save_settings()
        return db_path