from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets

from app.auth.jwt_handler import verify_access_token
from app.database.database import SessionLocal
from app.database.models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

security = HTTPBearer()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ================= DATABASE =================

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ================= CURRENT USER =================

def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)

):

    payload = verify_access_token(
        credentials.credentials
    )

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
        status_code=401,
        detail="Session expired. Please log in again."
    )

return user
  

# ================= SCHEMAS =================

class ProfileUpdate(BaseModel):

    name: str
    email: EmailStr


class PasswordUpdate(BaseModel):

    current_password: str
    new_password: str


class NotificationSettings(BaseModel):

    email_notifications: bool
    telegram_notifications: bool


class TelegramConnect(BaseModel):

    telegram_chat_id: str


# ================= USER PROFILE =================

@router.get("/me")
def get_me(

    current_user: User = Depends(get_current_user)

):

    return {

        "id": current_user.id,

        "name": getattr(current_user, "name", ""),

        "email": current_user.email,

        "role": current_user.role,

        "category": current_user.category,

        "telegram_connected":
            current_user.telegram_chat_id is not None,

        "telegram_chat_id":
            current_user.telegram_chat_id,

        "telegram_notifications":
            current_user.telegram_notifications,

        "email_notifications":
            current_user.email_notifications

    }


# ================= UPDATE PROFILE =================

@router.put("/profile")
def update_profile(

    data: ProfileUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    existing = (

        db.query(User)

        .filter(
            User.email == data.email,
            User.id != current_user.id
        )

        .first()

    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

    if hasattr(current_user, "name"):
        current_user.name = data.name

    current_user.email = data.email

    db.commit()

    db.refresh(current_user)

    return {

        "success": True,

        "message": "Profile updated successfully."

    }
# ================= CHANGE PASSWORD =================

@router.put("/change-password")
def change_password(

    data: PasswordUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    password_field = None

    if hasattr(current_user, "hashed_password"):
        password_field = "hashed_password"
    elif hasattr(current_user, "password"):
        password_field = "password"

    if password_field is None:

        raise HTTPException(
            status_code=500,
            detail="Password field not found."
        )

    stored_password = getattr(current_user, password_field)

    valid = False

    try:

        valid = pwd_context.verify(
            data.current_password,
            stored_password
        )

    except Exception:

        # fallback for old plain-text passwords
        valid = stored_password == data.current_password

    if not valid:

        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect."
        )

    new_hash = pwd_context.hash(
        data.new_password
    )

    setattr(
        current_user,
        password_field,
        new_hash
    )

    db.commit()

    return {

        "success": True,

        "message": "Password changed successfully."

    }


# ================= NOTIFICATION SETTINGS =================

@router.put("/notification-settings")
def update_notification_settings(

    data: NotificationSettings,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    current_user.email_notifications = (
        data.email_notifications
    )

    current_user.telegram_notifications = (
        data.telegram_notifications
    )

    db.commit()

    db.refresh(current_user)

    return {

        "success": True,

        "message": "Notification settings updated successfully."

    }
# ================= CONNECT TELEGRAM =================

@router.post("/connect-telegram")
def connect_telegram(

    data: TelegramConnect,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    current_user.telegram_chat_id = data.telegram_chat_id

    current_user.telegram_link_token = None

    current_user.telegram_notifications = True

    db.commit()

    db.refresh(current_user)

    return {

        "success": True,

        "message": "Telegram connected successfully."

    }


# ================= DISCONNECT TELEGRAM =================

@router.post("/disconnect-telegram")
def disconnect_telegram(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    current_user.telegram_chat_id = None

    current_user.telegram_link_token = None

    current_user.telegram_notifications = False

    db.commit()

    db.refresh(current_user)

    return {

        "success": True,

        "message": "Telegram disconnected successfully."

    }


# ================= GENERATE TELEGRAM LINK TOKEN =================

@router.get("/telegram-token")
def generate_telegram_token(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    token = secrets.token_urlsafe(32)

    current_user.telegram_link_token = token

    db.commit()

    return {

        "success": True,

        "token": token,

        "message": "Telegram link token generated."

    }


# ================= PROFILE DETAILS =================

@router.get("/profile")
def profile(

    current_user: User = Depends(get_current_user)

):

    return {

        "name": getattr(current_user, "name", ""),

        "email": current_user.email,

        "role": current_user.role,

        "category": current_user.category,

        "telegram_connected":
            current_user.telegram_chat_id is not None,

        "telegram_chat_id":
            current_user.telegram_chat_id,

        "email_notifications":
            current_user.email_notifications,

        "telegram_notifications":
            current_user.telegram_notifications

    }