from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Notice
from app.ai.gemini_service import summarize_notice
from app.services.notification_service import notify_users


def create_notice(data):

    db: Session = SessionLocal()

    try:

        # ---------------- Duplicate Check ----------------

        existing = (
            db.query(Notice)
            .filter(Notice.notice_url == data.notice_url)
            .first()
        )

        if existing:
            return existing

        # ---------------- AI Summary ----------------

        try:

            ai = summarize_notice(
                data.title,
                data.description
            )

        except Exception as e:

            print("Gemini Error:", e)

            ai = {

                "summary": data.description,

                "translated_summary": "",

                "important_dates": "",

                "eligibility": "",

                "action_required": "",

                "keywords": "",

                "priority": "LOW",

                "notice_type": "General",

                "deadline": None,

                "days_left": None

            }

        keywords = ai.get("keywords", "")

        if isinstance(keywords, list):
            keywords = ", ".join(keywords)

        # ---------------- Create Notice ----------------

        notice = Notice(

            title=data.title,

            description=data.description,

            category=data.category,

            source=data.source,

            notice_url=data.notice_url,

            summary=ai.get("summary"),

            translated_summary=ai.get(
                "translated_summary"
            ),

            important_dates=ai.get(
                "important_dates"
            ),

            eligibility=ai.get(
                "eligibility"
            ),

            action_required=ai.get(
                "action_required"
            ),

            keywords=keywords,

            priority=ai.get(
                "priority",
                "LOW"
            ),

            notice_type=ai.get(
                "notice_type",
                "General"
            ),

            deadline=ai.get(
                "deadline"
            ),

            days_left=ai.get(
                "days_left"
            ),

            is_ai_processed=True

        )

        db.add(notice)

        db.commit()

        db.refresh(notice)

        # ---------------- Notifications ----------------

        try:

            notify_users(db, notice)

        except Exception as e:

            print("Notification Error:", e)

        return notice

    finally:

        db.close()


def get_all_notices():

    db: Session = SessionLocal()

    try:

        return (

            db.query(Notice)

            .order_by(
                Notice.created_at.desc()
            )

            .all()

        )

    finally:

        db.close()


def get_notice_by_id(notice_id):

    db: Session = SessionLocal()

    try:

        return (

            db.query(Notice)

            .filter(
                Notice.id == notice_id
            )

            .first()

        )

    finally:

        db.close()


def delete_notice(notice_id):

    db: Session = SessionLocal()

    try:

        notice = (

            db.query(Notice)

            .filter(
                Notice.id == notice_id
            )

            .first()

        )

        if not notice:
            return False

        db.delete(notice)

        db.commit()

        return True

    finally:

        db.close()