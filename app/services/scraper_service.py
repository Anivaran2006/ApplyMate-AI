from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Notice

from app.ai.gemini_service import summarize_notice
from app.services.notification_service import notify_users

# ---------------- SCRAPERS ----------------

from app.scraper.nta_scraper import scrape_nta
from app.scraper.gate_scraper import scrape_gate
from app.scraper.upsc_scraper import scrape_upsc
from app.scraper.ssc_scraper import scrape_ssc
from app.scraper.banking_scraper import scrape_banking
from app.scraper.clat_scraper import scrape_clat

# Railway and CAT are temporarily disabled
# from app.scraper.railway_scraper import scrape_railway
# from app.scraper.cat_scraper import scrape_cat


SCRAPERS = [

    {
        "name": "NTA",
        "category": "JEE",
        "function": scrape_nta
    },

    {
        "name": "GATE",
        "category": "GATE",
        "function": scrape_gate
    },

    {
        "name": "UPSC",
        "category": "UPSC",
        "function": scrape_upsc
    },

    {
        "name": "SSC",
        "category": "SSC",
        "function": scrape_ssc
    },

    {
        "name": "Banking",
        "category": "BANKING",
        "function": scrape_banking
    },

    {
        "name": "CLAT",
        "category": "CLAT",
        "function": scrape_clat
    }

]


def process_notice(db: Session, scraper: dict, item: dict):

    existing = (
        db.query(Notice)
        .filter(Notice.notice_url == item["url"])
        .first()
    )

    if existing:
        return False

    try:

        ai = summarize_notice(
            item["title"],
            item.get("description", item["title"])
        )

    except Exception as e:

        print("Gemini Error:", e)

        ai = {
            "summary": item["title"],
            "translated_summary": "",
            "important_dates": "",
            "eligibility": "",
            "action_required": "",
            "keywords": [],
            "priority": "LOW",
            "notice_type": "General",
            "deadline": None,
            "days_left": None
        }

    keywords = ai.get("keywords", [])

    if isinstance(keywords, list):
        keywords = ", ".join(keywords)

    notice = Notice(

        title=item["title"],

        description=item.get(
            "description",
            item["title"]
        ),

        category=scraper["category"],

        source=scraper["name"],

        notice_url=item["url"],

        summary=ai["summary"],

        translated_summary=ai["translated_summary"],

        important_dates=ai["important_dates"],

        eligibility=ai["eligibility"],

        action_required=ai["action_required"],

        keywords=keywords,

        priority=ai["priority"],

        notice_type=ai["notice_type"],

        deadline=ai["deadline"],

        days_left=ai["days_left"],

        is_ai_processed=True

    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    try:

        notify_users(db, notice)

    except Exception as e:

        print("Notification Error:", e)

    return True


def scrape_and_save():

    db: Session = SessionLocal()

    added = 0
    skipped = 0

    try:

        for scraper in SCRAPERS:

            print("=" * 60)
            print(f"Checking {scraper['name']}")
            print("=" * 60)

            try:

                notices = scraper["function"]()

            except Exception as e:

                print(f"{scraper['name']} failed:", e)
                continue

            print(f"Found {len(notices)} notices")

            for item in notices:

                if process_notice(db, scraper, item):
                    added += 1
                else:
                    skipped += 1

        print("=" * 60)
        print("Scraping Finished")
        print(f"Added   : {added}")
        print(f"Skipped : {skipped}")
        print("=" * 60)

        return {
            "added": added,
            "skipped": skipped
        }

    finally:
        db.close()