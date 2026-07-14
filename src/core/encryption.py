from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
import base64
from src.core.config import settings

def get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if not key:
        # Generate a dummy key if none provided (for development/testing), but log a warning ideally.
        # Fernet keys must be 32 url-safe base64-encoded bytes.
        raise HTTPException(
            status_code=500, detail="ENCRYPTION_KEY is not configured in environment"
        )
    
    # Ensure key is valid length/format. If it's just a random string from user,
    # we should pad it or hash it. But since user said "our salt set in env", 
    # we assume they will provide a valid 32-byte base64 string. If not, let's auto-pad it.
    try:
        return Fernet(key.encode('utf-8'))
    except ValueError:
        # If the key isn't exactly 32 url-safe base64 encoded bytes, derive one from the raw string.
        import hashlib
        m = hashlib.sha256()
        m.update(key.encode('utf-8'))
        derived_key = base64.urlsafe_b64encode(m.digest())
        return Fernet(derived_key)

def encrypt(data: str) -> str:
    """Encrypts a string and returns a base64 encoded string."""
    if not data:
        return data
    f = get_fernet()
    return f.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    """Decrypts a base64 encoded encrypted string."""
    if not token:
        return token
    f = get_fernet()
    try:
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        raise ValueError("Invalid encryption token or key mismatch")
