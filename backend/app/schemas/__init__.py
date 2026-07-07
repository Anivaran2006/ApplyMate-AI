"""
ApplyMate AI – Pydantic Schemas Package
"""

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, NotificationSettings
from app.schemas.notice import NoticeResponse, NoticeListResponse, AIActionRequest
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.schemas.admin import AdminLoginRequest, AdminStats, UserAdminResponse

__all__ = [
    "SignupRequest", "LoginRequest", "TokenResponse", "RefreshRequest",
    "ForgotPasswordRequest", "ResetPasswordRequest",
    "UserResponse", "UserUpdate", "PasswordChange", "NotificationSettings",
    "NoticeResponse", "NoticeListResponse", "AIActionRequest",
    "SubscriptionCreate", "SubscriptionResponse",
    "AdminLoginRequest", "AdminStats", "UserAdminResponse",
]
