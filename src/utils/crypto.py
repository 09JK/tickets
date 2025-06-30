"""
Cryptography utilities for encrypting/decrypting sensitive data.
"""

import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

logger = logging.getLogger(__name__)


class CryptoManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self, password: Optional[str] = None):
        """Initialize crypto manager with password."""
        self.password = password or os.environ.get("ENCRYPTION_KEY", "default-key")
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if self._fernet is None:
            # Generate key from password
            password_bytes = self.password.encode()
            salt = b"discord_tickets_salt"  # In production, use a random salt
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt(self, text: str) -> str:
        """Encrypt text and return base64 encoded string."""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = fernet.encrypt(text.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return text
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded encrypted text."""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_text


# Global crypto manager instance
_crypto_manager = None


def get_crypto_manager() -> CryptoManager:
    """Get global crypto manager instance."""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager


def encrypt_text(text: str) -> str:
    """Encrypt text using global crypto manager."""
    return get_crypto_manager().encrypt(text)


def decrypt_text(encrypted_text: str) -> str:
    """Decrypt text using global crypto manager."""
    return get_crypto_manager().decrypt(encrypted_text)