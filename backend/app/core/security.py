import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}${h.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        salt, expected = hashed.split("$", 1)
        h = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100000)
        return h.hex() == expected
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        return None


def generate_challenge() -> str:
    return secrets.token_hex(32)


def compute_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def compute_identity_hash(did: str, public_key: str, algorithm: str) -> str:
    payload = f"{did}:{public_key}:{algorithm}"
    return compute_hash(payload)


def generate_did() -> str:
    return f"did:qidentity:{secrets.token_hex(16)}"
