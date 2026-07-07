"""
ApplyMate AI – User Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import (
    NotificationSettings,
    PasswordChange,
    TelegramConnectRequest,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    change_password,
    connect_telegram,
    update_notification_settings,
    update_user_profile,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile fields."""
    user = await update_user_profile(db, current_user, data)
    await db.commit()
    return user


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password_endpoint(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password."""
    success = await change_password(db, current_user, data.current_password, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    await db.commit()
    return {"message": "Password updated successfully"}


@router.put("/me/notifications", response_model=UserResponse)
async def update_notifications(
    data: NotificationSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable/disable email and Telegram notifications."""
    user = await update_notification_settings(db, current_user, data)
    await db.commit()
    return user


@router.post("/me/telegram/connect", status_code=status.HTTP_200_OK)
async def connect_telegram_endpoint(
    data: TelegramConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Link a Telegram chat_id to the user account."""
    await connect_telegram(db, current_user, data.chat_id)
    await db.commit()
    return {"message": "Telegram connected successfully"}


@router.delete("/me/telegram", status_code=status.HTTP_200_OK)
async def disconnect_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlink Telegram from the user account."""
    current_user.telegram_chat_id = None
    current_user.telegram_notifications = False
    await db.commit()
    return {"message": "Telegram disconnected"}
