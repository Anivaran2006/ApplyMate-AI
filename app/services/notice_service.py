from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Notice
from app.ai.gemini_service import summarize_notice

def create_notice(data):

    db: Session = SessionLocal()

    try:

        # Generate AI summary
        ai = summarize_notice(
            data.title,
            data.description
        )

        # Create notice with AI fields
        notice = Notice(

            title=data.title,

            description=data.description,

            category=data.category,

            source=data.source,

            notice_url=data.notice_url,

            summary=ai["summary"],

            important_dates=ai["important_dates"],

            eligibility=ai["eligibility"],

            action_required=ai["action_required"],

            keywords=ai["keywords"],

            is_ai_processed=True

        )

        db.add(notice)

        db.commit()

        db.refresh(notice)

        return notice

    finally:

        db.close()

def get_all_notices():

    db: Session = SessionLocal()

    try:

        return db.query(Notice).all()

    finally:

        db.close()


def get_notice_by_id(notice_id):

    db: Session = SessionLocal()

    try:

        return (
            db.query(Notice)
            .filter(Notice.id == notice_id)
            .first()
        )

    finally:

        db.close()


def delete_notice(notice_id):

    db: Session = SessionLocal()

    try:

        notice = (
            db.query(Notice)
            .filter(Notice.id == notice_id)
            .first()
        )

        if not notice:
            return False

        db.delete(notice)

        db.commit()

        return True

    finally:

        db.close()