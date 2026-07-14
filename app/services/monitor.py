from app.services.scraper_service import scrape_and_save


def monitor():

    print("=" * 60)
    print("🚀 ApplyMate AI Scheduler Triggered")
    print("=" * 60)

    try:

        result = scrape_and_save()

        print(f"✅ Added Notices   : {result['added']}")
        print(f"⏭️ Skipped Notices : {result['skipped']}")

        return {
            "status": "SUCCESS",
            "added": result["added"],
            "skipped": result["skipped"]
        }

    except Exception as e:

        print("❌ Scheduler Error:", e)

        return {
            "status": "FAILED",
            "error": str(e)
        }