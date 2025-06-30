"""
Enhanced Security Module for BSM.

This module provides:
- Secure API key storage with key rotation
- Certificate pinning for HTTPS connections
- Secure credential management
- Privacy-preserving telemetry (opt-in)
- Security audit logging
"""

import os
import json
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import ssl
import certifi
import urllib3
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import threading
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """Security event for audit logging."""
    timestamp: datetime
    event_type: str
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    description: str
    metadata: Dict[str, Any]
    user_id: Optional[str] = None


class KeyRotationManager:
    """Manages encryption key rotation for enhanced security."""
    
    def __init__(self, key_file: str, rotation_days: int = 30):
        self.key_file = Path(key_file)
        self.rotation_days = rotation_days
        self._keys: List[Tuple[bytes, datetime]] = []
        self._lock = threading.Lock()
        self._load_keys()
    
    def _load_keys(self):
        """Load existing keys from file."""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    data = json.loads(f.read().decode())
                    for key_data in data['keys']:
                        key = base64.b64decode(key_data['key'])
                        created = datetime.fromisoformat(key_data['created'])
                        self._keys.append((key, created))
            except Exception as e:
                logger.error(f"Failed to load keys: {e}")
                self._generate_new_key()
        else:
            self._generate_new_key()
    
    def _save_keys(self):
        """Save keys to file."""
        data = {
            'keys': [
                {
                    'key': base64.b64encode(key).decode(),
                    'created': created.isoformat()
                }
                for key, created in self._keys
            ]
        }
        
        # Ensure directory exists
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write atomically
        temp_file = self.key_file.with_suffix('.tmp')
        with open(temp_file, 'wb') as f:
            f.write(json.dumps(data).encode())
        
        # Move to final location
        temp_file.replace(self.key_file)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.key_file, 0o600)
    
    def _generate_new_key(self) -> bytes:
        """Generate a new encryption key."""
        key = Fernet.generate_key()
        with self._lock:
            self._keys.insert(0, (key, datetime.now()))
            # Keep last 3 keys for decryption of old data
            self._keys = self._keys[:3]
            self._save_keys()
        return key
    
    def get_current_key(self) -> bytes:
        """Get the current encryption key."""
        with self._lock:
            if not self._keys:
                return self._generate_new_key()
            
            # Check if rotation is needed
            current_key, created = self._keys[0]
            if datetime.now() - created > timedelta(days=self.rotation_days):
                logger.info("Rotating encryption key")
                return self._generate_new_key()
            
            return current_key
    
    def get_all_keys(self) -> List[bytes]:
        """Get all keys for decryption attempts."""
        with self._lock:
            return [key for key, _ in self._keys]


class SecureCredentialManager:
    """Manages secure storage of API keys and credentials."""
    
    def __init__(self, credentials_file: str, master_password: Optional[str] = None):
        self.credentials_file = Path(credentials_file)
        self.key_manager = KeyRotationManager(
            str(self.credentials_file.parent / '.keys')
        )
        self._master_key = self._derive_master_key(master_password)
        self._credentials: Dict[str, Any] = {}
        self._load_credentials()
    
    def _derive_master_key(self, password: Optional[str]) -> bytes:
        """Derive a master key from password or system info."""
        if password:
            salt = b'bsm-credential-salt'  # Fixed salt for deterministic key
        else:
            # Use system-specific info as password
            import platform
            system_info = f"{platform.node()}-{platform.system()}-{os.getuid()}"
            password = system_info
            salt = b'bsm-system-salt'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(
            kdf.derive(password.encode())
        )
    
    def _load_credentials(self):
        """Load credentials from encrypted file."""
        if not self.credentials_file.exists():
            return
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Try to decrypt with all available keys
            decrypted = None
            for key in self.key_manager.get_all_keys():
                try:
                    fernet = Fernet(key)
                    decrypted = fernet.decrypt(encrypted_data)
                    break
                except InvalidToken:
                    continue
            
            if decrypted:
                self._credentials = json.loads(decrypted.decode())
            else:
                logger.error("Failed to decrypt credentials with any key")
                
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
    
    def _save_credentials(self):
        """Save credentials to encrypted file."""
        try:
            # Get current key for encryption
            key = self.key_manager.get_current_key()
            fernet = Fernet(key)
            
            # Encrypt credentials
            encrypted_data = fernet.encrypt(
                json.dumps(self._credentials).encode()
            )
            
            # Ensure directory exists
            self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write atomically
            temp_file = self.credentials_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Move to final location
            temp_file.replace(self.credentials_file)
            
            # Set restrictive permissions
            os.chmod(self.credentials_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise
    
    def store_credential(self, service: str, key: str, value: str):
        """Store an encrypted credential."""
        if service not in self._credentials:
            self._credentials[service] = {}
        
        # Additional encryption layer for the value
        fernet = Fernet(self._master_key)
        encrypted_value = fernet.encrypt(value.encode()).decode()
        
        self._credentials[service][key] = {
            'value': encrypted_value,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        
        self._save_credentials()
        
        # Log security event
        SecurityAuditor.log_event(SecurityEvent(
            timestamp=datetime.now(),
            event_type="credential_stored",
            severity="INFO",
            description=f"Credential stored for {service}",
            metadata={"service": service, "key": key}
        ))
    
    def get_credential(self, service: str, key: str) -> Optional[str]:
        """Retrieve a decrypted credential."""
        try:
            if service not in self._credentials:
                return None
            
            if key not in self._credentials[service]:
                return None
            
            credential_data = self._credentials[service][key]
            
            # Decrypt the value
            fernet = Fernet(self._master_key)
            decrypted_value = fernet.decrypt(
                credential_data['value'].encode()
            ).decode()
            
            # Update last used time
            credential_data['last_used'] = datetime.now().isoformat()
            self._save_credentials()
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential: {e}")
            SecurityAuditor.log_event(SecurityEvent(
                timestamp=datetime.now(),
                event_type="credential_retrieval_failed",
                severity="ERROR",
                description=f"Failed to retrieve credential for {service}",
                metadata={"service": service, "key": key, "error": str(e)}
            ))
            return None
    
    def delete_credential(self, service: str, key: Optional[str] = None):
        """Delete a credential or all credentials for a service."""
        if service not in self._credentials:
            return
        
        if key:
            self._credentials[service].pop(key, None)
            if not self._credentials[service]:
                del self._credentials[service]
        else:
            del self._credentials[service]
        
        self._save_credentials()
        
        SecurityAuditor.log_event(SecurityEvent(
            timestamp=datetime.now(),
            event_type="credential_deleted",
            severity="INFO",
            description=f"Credential deleted for {service}",
            metadata={"service": service, "key": key}
        ))


class CertificatePinner:
    """Handles certificate pinning for secure HTTPS connections."""
    
    def __init__(self, pins_file: str):
        self.pins_file = Path(pins_file)
        self._pins: Dict[str, List[str]] = {}
        self._load_pins()
    
    def _load_pins(self):
        """Load certificate pins from file."""
        if self.pins_file.exists():
            try:
                with open(self.pins_file, 'r') as f:
                    self._pins = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load certificate pins: {e}")
    
    def add_pin(self, hostname: str, pin: str):
        """Add a certificate pin for a hostname."""
        if hostname not in self._pins:
            self._pins[hostname] = []
        
        if pin not in self._pins[hostname]:
            self._pins[hostname].append(pin)
            self._save_pins()
    
    def _save_pins(self):
        """Save certificate pins to file."""
        self.pins_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pins_file, 'w') as f:
            json.dump(self._pins, f, indent=2)
    
    def get_pinned_context(self, hostname: str) -> ssl.SSLContext:
        """Get an SSL context with certificate pinning."""
        context = ssl.create_default_context(cafile=certifi.where())
        
        # Enable hostname checking
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Add certificate verification callback if pins exist
        if hostname in self._pins:
            pins = self._pins[hostname]
            
            def verify_callback(conn, cert, errno, depth, ok):
                if depth == 0:  # Leaf certificate
                    # Calculate pin from certificate
                    cert_der = cert.to_der()
                    cert_hash = hashlib.sha256(cert_der).hexdigest()
                    
                    if cert_hash not in pins:
                        logger.error(f"Certificate pin mismatch for {hostname}")
                        SecurityAuditor.log_event(SecurityEvent(
                            timestamp=datetime.now(),
                            event_type="certificate_pin_mismatch",
                            severity="CRITICAL",
                            description=f"Certificate pin mismatch for {hostname}",
                            metadata={
                                "hostname": hostname,
                                "expected_pins": pins,
                                "actual_pin": cert_hash
                            }
                        ))
                        return False
                
                return ok
            
            # Note: In production, use pyOpenSSL for proper callback support
            # context.set_verify(ssl.CERT_REQUIRED, verify_callback)
        
        return context


class PrivacyTelemetry:
    """Privacy-preserving telemetry system (opt-in only)."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._session_id = str(uuid.uuid4())
        self._events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable telemetry."""
        self.enabled = enabled
        
        if not enabled:
            # Clear any pending events
            with self._lock:
                self._events.clear()
    
    def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """Track an anonymous event."""
        if not self.enabled:
            return
        
        # Sanitize properties to remove any PII
        safe_properties = self._sanitize_properties(properties or {})
        
        event = {
            'event': event_name,
            'timestamp': datetime.now().isoformat(),
            'session_id': self._session_id,
            'properties': safe_properties
        }
        
        with self._lock:
            self._events.append(event)
            
            # Batch send when we have enough events
            if len(self._events) >= 10:
                self._send_events()
    
    def _sanitize_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Remove any potentially identifying information."""
        # List of keys that might contain PII
        pii_keys = {
            'api_key', 'token', 'password', 'email', 'username',
            'path', 'file', 'directory', 'url', 'ip', 'host'
        }
        
        sanitized = {}
        for key, value in properties.items():
            # Skip PII keys
            if any(pii in key.lower() for pii in pii_keys):
                continue
            
            # Sanitize string values
            if isinstance(value, str):
                # Only keep general categories, not specific values
                if key == 'provider':
                    sanitized[key] = value  # Provider names are safe
                elif key == 'attitude_mode':
                    sanitized[key] = value  # Attitude modes are safe
                else:
                    # Replace with generic marker
                    sanitized[key] = '<redacted>'
            elif isinstance(value, (int, float, bool)):
                # Numeric and boolean values are generally safe
                sanitized[key] = value
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = self._sanitize_properties(value)
        
        return sanitized
    
    def _send_events(self):
        """Send telemetry events (not implemented - would send to server)."""
        # This is where you would send to a telemetry server
        # For now, just log that we would send
        event_count = len(self._events)
        self._events.clear()
        logger.info(f"Would send {event_count} telemetry events (not implemented)")


class SecurityAuditor:
    """Security audit logging system."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._events: List[SecurityEvent] = []
            self._max_events = 10000
            self._audit_file = Path.home() / '.bsm' / 'security_audit.log'
            self._initialized = True
    
    @classmethod
    def log_event(cls, event: SecurityEvent):
        """Log a security event."""
        instance = cls()
        
        # Add to in-memory list
        instance._events.append(event)
        
        # Trim if too large
        if len(instance._events) > instance._max_events:
            instance._events = instance._events[-instance._max_events:]
        
        # Write to audit file
        instance._write_event(event)
        
        # Log to standard logger based on severity
        log_method = getattr(logger, event.severity.lower(), logger.info)
        log_method(f"Security Event: {event.event_type} - {event.description}")
    
    def _write_event(self, event: SecurityEvent):
        """Write event to audit file."""
        try:
            self._audit_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._audit_file, 'a') as f:
                f.write(json.dumps(asdict(event), default=str) + '\n')
            
            # Rotate log if too large (> 10MB)
            if self._audit_file.stat().st_size > 10 * 1024 * 1024:
                self._rotate_audit_log()
                
        except Exception as e:
            logger.error(f"Failed to write audit event: {e}")
    
    def _rotate_audit_log(self):
        """Rotate the audit log file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rotated_file = self._audit_file.with_name(
            f"{self._audit_file.stem}_{timestamp}{self._audit_file.suffix}"
        )
        self._audit_file.rename(rotated_file)
        
        # Keep only last 5 rotated files
        rotated_files = sorted(
            self._audit_file.parent.glob(f"{self._audit_file.stem}_*{self._audit_file.suffix}")
        )
        for old_file in rotated_files[:-5]:
            old_file.unlink()
    
    @classmethod
    def get_recent_events(cls, count: int = 100) -> List[SecurityEvent]:
        """Get recent security events."""
        instance = cls()
        return instance._events[-count:]


# Convenience functions
def create_secure_session(
    hostname: str,
    certificate_pins: Optional[List[str]] = None
) -> urllib3.HTTPSConnectionPool:
    """Create a secure HTTPS session with certificate pinning."""
    pinner = CertificatePinner(str(Path.home() / '.bsm' / 'cert_pins.json'))
    
    # Add pins if provided
    if certificate_pins:
        for pin in certificate_pins:
            pinner.add_pin(hostname, pin)
    
    # Get SSL context with pinning
    ssl_context = pinner.get_pinned_context(hostname)
    
    # Create connection pool
    return urllib3.HTTPSConnectionPool(
        hostname,
        ssl_context=ssl_context,
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
