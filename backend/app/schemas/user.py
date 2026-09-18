"""
ApplyMate AI – User Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    email_notifications: bool
    telegram_notifications: bool
    telegram_chat_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    def has_updates(self) -> bool:
        return any(v is not None for v in self.model_dump().values())


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class NotificationSettings(BaseModel):
    email_notifications: Optional[bool] = None
    telegram_notifications: Optional[bool] = None
    telegram_chat_id: Optional[str] = None


class TelegramConnectRequest(BaseModel):
    chat_id: str
