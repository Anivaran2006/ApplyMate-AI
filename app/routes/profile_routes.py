from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User
from app.auth.jwt_handler import verify_access_token
from app.auth.security import hash_password

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    payload = verify_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.email == payload["sub"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


class ProfileUpdate(BaseModel):
    email_notifications: bool
    telegram_notifications: bool


class PasswordUpdate(BaseModel):
    password: str


@router.get("/")
def profile(
    current_user: User = Depends(get_current_user)
):

    return {
        "email": current_user.email,
        "role": current_user.role,
        "category": current_user.category,
        "telegram_connected": current_user.telegram_chat_id is not None,
        "telegram_notifications": current_user.telegram_notifications,
        "email_notifications": current_user.email_notifications
    }


@router.put("/settings")
def update_settings(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    current_user.email_notifications = data.email_notifications
    current_user.telegram_notifications = data.telegram_notifications

    db.commit()

    return {
        "message": "Settings updated."
    }


@router.put("/password")
def change_password(
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    current_user.password = hash_password(data.password)

    db.commit()

    return {
        "message": "Password changed successfully."
    }