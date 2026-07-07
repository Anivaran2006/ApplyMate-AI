"""
ApplyMate AI – Auth Service
Business logic for signup, login, token management, and password reset.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.models.admin import Admin
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def signup_user(db: AsyncSession, data: SignupRequest) -> User:
    """Register a new user. Raises ValueError on duplicate email."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()
    logger.info(f"New user registered: {user.email}")
    return user


async def login_user(db: AsyncSession, data: LoginRequest) -> Optional[TokenResponse]:
    """Authenticate user and return tokens. Returns None on invalid credentials."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        return None

    if not user.is_active:
        raise ValueError("Account is deactivated")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
    )


async def login_admin(db: AsyncSession, email: str, password: str) -> Optional[TokenResponse]:
    """Authenticate admin. Returns None on invalid credentials."""
    result = await db.execute(select(Admin).where(Admin.email == email))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(password, admin.hashed_password):
        return None

    return TokenResponse(
        access_token=create_access_token(admin.id),
        refresh_token=create_refresh_token(admin.id),
        token_type="bearer",
        user_id=admin.id,
        full_name="Admin",
        email=admin.email,
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Optional[TokenResponse]:
    """Issue new access/refresh tokens from a valid refresh token."""
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
    )


async def initiate_password_reset(db: AsyncSession, email: str) -> Optional[str]:
    """Generate a reset token for the given email. Returns token or None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    await db.flush()
    return token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> bool:
    """Reset password using a valid reset token. Returns True on success."""
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires:
        return False

    if user.reset_token_expires < datetime.now(timezone.utc):
        return False

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.flush()
    return True


async def create_initial_admin(db: AsyncSession, email: str, password: str) -> Admin:
    """Create the first admin account on startup if none exists."""
    result = await db.execute(select(Admin).where(Admin.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    admin = Admin(
        email=email,
        hashed_password=hash_password(password),
        is_superadmin=True,
    )
    db.add(admin)
    await db.flush()
    logger.info(f"Admin account created: {email}")
    return admin
