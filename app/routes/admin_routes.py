from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User, Notice
from app.services.scraper_service import scrape_and_save

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/notices/scrape-now")
def scrape_now():

    result = scrape_and_save()

    return {
        "message": "Scraping completed successfully.",
        "added": result["added"],
        "skipped": result["skipped"]
    }


@router.get("/stats")
def get_stats():

    db: Session = SessionLocal()

    try:

        total_users = db.query(User).count()

        total_notices = db.query(Notice).count()

        processed_notices = (
            db.query(Notice)
            .filter(Notice.is_ai_processed == True)
            .count()
        )

        return {
            "total_users": total_users,
            "active_users": total_users,
            "total_notices": total_notices,
            "processed_notices": processed_notices,
            "total_notifications_sent": 0,
            "telegram_connected_users": 0
        }

    finally:
        db.close()