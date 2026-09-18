"""
ApplyMate AI – Security Utilities
Handles password hashing, JWT creation/verification, and token models.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import JWTError, jwt
import bcrypt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return bcrypt hash of the plain password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        try:
            return pwd_context.verify(plain_password[:72], hashed_password)
        except Exception:
            return False


# ── JWT ───────────────────────────────────────────────────────────────────────
def _create_token(
    subject: Union[str, Any],
    token_type: str,
    expires_delta: timedelta,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: Union[str, Any]) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: Union[str, Any]) -> str:
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT.
    Returns the payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[str]:
    """Return user id (sub) from a valid access token, else None."""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload.get("sub")
    return None


def verify_refresh_token(token: str) -> Optional[str]:
    """Return user id (sub) from a valid refresh token, else None."""
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload.get("sub")
    return None
