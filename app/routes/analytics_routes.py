from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import (
    User,
    Notice,
    Subscription
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def analytics(
    db: Session = Depends(get_db)
):

    total_users = db.query(User).count()

    total_notices = db.query(Notice).count()

    total_subscriptions = db.query(
        Subscription
    ).count()

    telegram_connected = (
        db.query(User)
        .filter(User.telegram_chat_id != None)
        .count()
    )

    email_enabled = (
        db.query(User)
        .filter(User.email_notifications == True)
        .count()
    )

    telegram_enabled = (
        db.query(User)
        .filter(User.telegram_notifications == True)
        .count()
    )

    category_counts = {}

    for sub in db.query(Subscription).all():

        category_counts[sub.category] = (
            category_counts.get(sub.category, 0) + 1
        )

    return {

        "total_users": total_users,

        "total_notices": total_notices,

        "total_subscriptions": total_subscriptions,

        "telegram_connected": telegram_connected,

        "email_enabled": email_enabled,

        "telegram_enabled": telegram_enabled,

        "popular_categories": category_counts

    }