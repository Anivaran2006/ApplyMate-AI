"""
ApplyMate AI – Admin Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_notices: int
    processed_notices: int
    total_notifications_sent: int
    telegram_connected_users: int


class UserAdminResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    telegram_chat_id: Optional[str]
    email_notifications: bool
    telegram_notifications: bool
    subscription_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ManualNotifyRequest(BaseModel):
    notice_id: int
    channel: str = "all"  # "telegram" | "email" | "all"


class ExportFilters(BaseModel):
    is_active: Optional[bool] = None
    category: Optional[str] = None
