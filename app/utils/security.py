from datetime import datetime, timedelta, timezone
import jwt
from cryptography.fernet import Fernet, InvalidToken
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()
fernet = Fernet(settings.FERNET_KEY.encode())

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hash.verify(password, hashed)
    except Exception:
        return False

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"require": ["exp", "iat", "sub"]})

# GitHub OAuth callback	
def encrypt_secret(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()
    
# GitHub repositories and branches APIs
def decrypt_secret(value: str) -> str:
    try:
        return fernet.decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Stored GitHub credential could not be decrypted") from exc
