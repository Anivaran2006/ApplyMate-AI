from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_access_token
from app.database.database import SessionLocal
from app.database.models import User
from app.services.telegram_auth_service import generate_telegram_token

router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"]
)

security = HTTPBearer()

# Replace with your actual bot username (NO @)
BOT_USERNAME = "ApplyMateAIaniv_bot"


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


@router.get("/connect")
def connect_telegram(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    token = generate_telegram_token(
        db,
        current_user.id
    )

    if token is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to generate Telegram token."
        )

    return {
        "success": True,
        "telegram_url": f"https://t.me/{BOT_USERNAME}?start={token}",
        "message": "Open this URL and press Start to connect your Telegram account."
    }
@router.get("/test")
def telegram_test():
    return {
        "message": "Telegram router is working"
    }