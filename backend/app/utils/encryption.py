"""Encryption utilities for sensitive data."""
from cryptography.fernet import Fernet
from app.config import settings
import base64


def get_fernet() -> Fernet:
    """
    Get Fernet cipher instance.

    Returns:
        Fernet: Fernet cipher instance
    """
    # Ensure the encryption key is properly formatted
    key = settings.ENCRYPTION_KEY.encode()
    # Convert to base64 if needed (Fernet requires base64-encoded 32-byte key)
    if len(key) == 32:
        key = base64.urlsafe_b64encode(key)
    return Fernet(key)


def encrypt_string(plaintext: str) -> str:
    """
    Encrypt a string.

    Args:
        plaintext: String to encrypt

    Returns:
        str: Encrypted string (base64 encoded)
    """
    f = get_fernet()
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_string(encrypted: str) -> str:
    """
    Decrypt a string.

    Args:
        encrypted: Encrypted string (base64 encoded)

    Returns:
        str: Decrypted plaintext string
    """
    f = get_fernet()
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()
