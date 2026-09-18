"""
ApplyMate AI – Auth Routes (FastAPI & SQLAlchemy Async)
"""

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app.core.database import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.services.auth_service import (
    initiate_password_reset,
    login_user,
    refresh_tokens,
    reset_password,
    signup_user,
)
from app.notifications.email import send_welcome_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register a new student account."""
    try:
        user = await signup_user(db, data)
        await db.commit()
        # Send welcome email (non-blocking)
        try:
            await send_welcome_email(user.email, user.full_name)
        except Exception:
            pass

        from app.core.security import create_access_token, create_refresh_token
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            token_type="bearer",
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT tokens."""
    try:
        tokens = await login_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Get new tokens from a valid refresh token."""
    tokens = await refresh_tokens(db, data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Initiate password reset (sends email in production)."""
    token = await initiate_password_reset(db, data.email)
    if token:
        await db.commit()
        try:
            await send_reset_password_email(to_email=data.email, token=token)
        except Exception:
            pass
    # Always return 200 to prevent email enumeration
    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_endpoint(
    data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Reset password using the token from the forgot-password email."""
    success = await reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    await db.commit()
    return {"message": "Password reset successfully"}
