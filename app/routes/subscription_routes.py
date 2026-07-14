from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User, Subscription
from app.auth.jwt_handler import verify_access_token

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
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


# ================= SCHEMA =================

class SubscriptionRequest(BaseModel):
    category: str


# ================= GET SUBSCRIPTIONS =================

@router.get("/")
def get_subscriptions(
    current_user: User = Depends(get_current_user)
):

    return [

        {
            "id": s.id,
            "category": s.category
        }

        for s in current_user.subscriptions

    ]


# ================= ADD SUBSCRIPTION =================

@router.post("/")
def add_subscription(

    data: SubscriptionRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    category = data.category.strip().upper()

    existing = (

        db.query(Subscription)

        .filter(
            Subscription.user_id == current_user.id,
            Subscription.category == category
        )

        .first()

    )

    if existing:

        return {

            "success": False,

            "message": "Already subscribed.",

            "subscription": {

                "id": existing.id,

                "category": existing.category

            }

        }

    sub = Subscription(

        user_id=current_user.id,

        category=category

    )

    db.add(sub)

    db.commit()

    db.refresh(sub)

    return {

        "success": True,

        "message": "Subscription added successfully.",

        "subscription": {

            "id": sub.id,

            "category": sub.category

        }

    }


# ================= REMOVE SUBSCRIPTION =================

@router.delete("/{category}")
def remove_subscription(

    category: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    category = category.strip().upper()

    sub = (

        db.query(Subscription)

        .filter(
            Subscription.user_id == current_user.id,
            Subscription.category == category
        )

        .first()

    )

    if not sub:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    db.delete(sub)

    db.commit()

    return {

        "success": True,

        "message": "Subscription removed successfully."

    }