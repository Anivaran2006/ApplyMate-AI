from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import (
    User,
    Notice,
    Subscription
)

from app.auth.jwt_handler import verify_access_token

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

security = HTTPBearer()


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
            status_code=404,
            detail="User not found"
        )

    return user


# ================= DASHBOARD STATS =================

@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    subscriptions = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user.id
        )
        .all()
    )

    latest_notices = (
        db.query(Notice)
        .order_by(
            Notice.created_at.desc()
        )
        .limit(10)
        .all()
    )

    return {

        "user": {

            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "category": current_user.category,

            "telegram_connected":
                current_user.telegram_chat_id is not None,

            "telegram_notifications":
                current_user.telegram_notifications,

            "email_notifications":
                current_user.email_notifications

        },

        "subscriptions": [
            s.category
            for s in subscriptions
        ],

        "latest_notices": [

            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "summary": n.summary,
                "url": n.notice_url,
                "priority": n.priority,
                "notice_type": n.notice_type,
                "deadline": n.deadline,
                "days_left": n.days_left,
                "created_at": n.created_at
            }

            for n in latest_notices

        ],

        "stats": {

            "total_notices": db.query(Notice).count(),

            "total_subscriptions": len(subscriptions),

            "telegram_connected":
                current_user.telegram_chat_id is not None

        }

    }