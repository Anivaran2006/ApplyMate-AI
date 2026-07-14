from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User, NotificationHistory
from app.auth.jwt_handler import verify_access_token

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
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

        .filter(
            User.email == payload["sub"]
        )

        .first()

    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ================= NOTIFICATION HISTORY =================

@router.get("/history")
def notification_history(

    page: int = 1,

    limit: int = 10,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    query = (

        db.query(NotificationHistory)

        .filter(
            NotificationHistory.user_id == current_user.id
        )

        .order_by(
            NotificationHistory.sent_at.desc()
        )

    )

    total = query.count()

    history = (

        query

        .offset((page - 1) * limit)

        .limit(limit)

        .all()

    )

    return {

        "items": [

            {

                "title": h.notice.title,

                "category": h.notice.category,

                "summary": h.notice.summary,

                "sent_via": h.sent_via,

                "sent_at": h.sent_at

            }

            for h in history

        ],

        "page": page,

        "limit": limit,

        "total": total,

        "pages": (
            (total + limit - 1) // limit
        )

    }