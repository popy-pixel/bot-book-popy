crypto_py = r'''"""
BOT-BOOK-POPY Crypto Utilities
===============================
Encryption/decryption for sensitive data (passwords, cookies).

Uses Fernet symmetric encryption from cryptography library.
Key should be provided via ENCRYPTION_KEY env var.
"""

import os
import base64
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from app.config import ENCRYPTION_KEY


class CryptoManager:
    """Manages encryption of sensitive account data."""

    def __init__(self, key: Optional[str] = None):
        self._fernet = None
        raw_key = key or ENCRYPTION_KEY

        if CRYPTO_AVAILABLE and raw_key:
            # Derive a proper Fernet key from the provided key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'bot-book-popy-salt',
                iterations=100000,
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(raw_key.encode()))
            self._fernet = Fernet(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string. Returns base64-encoded ciphertext."""
        if not self._fernet:
            # Fallback: base64 encode (not secure, but functional)
            return base64.b64encode(plaintext.encode()).decode()
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        if not self._fernet:
            return base64.b64decode(ciphertext.encode()).decode()
        return self._fernet.decrypt(ciphertext.encode()).decode()

    def is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted."""
        if not value:
            return False
        try:
            # Fernet tokens start with 'gAAAA'
            return value.startswith('gAAAA')
        except Exception:
            return False


# Singleton
crypto_manager = CryptoManager()


def encrypt_password(password: str) -> str:
    return crypto_manager.encrypt(password)


def decrypt_password(ciphertext: str) -> str:
    return crypto_manager.decrypt(ciphertext)
'''