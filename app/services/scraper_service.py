from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Notice

from app.scraper.nta_scraper import scrape_nta
from app.ai.gemini_service import summarize_notice


def scrape_and_save():

    db: Session = SessionLocal()

    added = 0
    skipped = 0

    try:

        # Process only first 3 notices during development
        notices = scrape_nta()[:3]

        for item in notices:

            existing = (
                db.query(Notice)
                .filter(Notice.notice_url == item["url"])
                .first()
            )

            if existing:
                skipped += 1
                continue

            # Generate AI summary
            try:

                ai = summarize_notice(
                    item["title"],
                    item["title"]
                )

            except Exception as e:

                print("Gemini Error:", e)

                ai = {
                    "summary": item["title"],
                    "important_dates": "",
                    "eligibility": "",
                    "action_required": "",
                    "keywords": ""
                }

            notice = Notice(

                title=item["title"],

                description=item["title"],

                category="JEE",

                source="NTA Scraper",

                notice_url=item["url"],

                summary=ai["summary"],

                important_dates=ai["important_dates"],

                eligibility=ai["eligibility"],

                action_required=ai["action_required"],

                keywords=", ".join(ai["keywords"]) if isinstance(ai["keywords"], list) else ai["keywords"],

                is_ai_processed=True

            )

            db.add(notice)

            added += 1

        db.commit()

        return {
            "added": added,
            "skipped": skipped
        }

    finally:

        db.close()