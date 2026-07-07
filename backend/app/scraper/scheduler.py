"""
ApplyMate AI – APScheduler Setup
Runs the scrape → AI process → notify pipeline on a configurable interval.
"""

import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="UTC")


async def run_scrape_pipeline() -> None:
    """
    Full pipeline:
    1. Scrape NTA for new notices
    2. Store new ones in DB
    3. Generate AI summaries
    4. Notify subscribed users
    """
    from app.core.database import AsyncSessionLocal
    from app.services.notice_service import process_scraped_notices
    from app.scraper.nta_scraper import scrape_nta

    logger.info("⏰ Scheduler: starting scrape pipeline...")
    start = datetime.now(timezone.utc)

    try:
        raw_notices = await scrape_nta()
        if not raw_notices:
            logger.warning("Scheduler: no notices returned from scraper")
            return

        async with AsyncSessionLocal() as db:
            new_count = await process_scraped_notices(db, raw_notices)
            logger.info(f"Scheduler: pipeline complete — {new_count} new notices processed")

    except Exception as e:
        logger.error(f"Scheduler pipeline error: {e}", exc_info=True)

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    logger.info(f"Scheduler: pipeline finished in {elapsed:.1f}s")


def start_scheduler() -> None:
    """Start the APScheduler with the configured interval."""
    if _scheduler.running:
        return

    interval_minutes = settings.SCRAPER_INTERVAL_MINUTES

    _scheduler.add_job(
        run_scrape_pipeline,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="scrape_pipeline",
        name="NTA Scrape & Notify Pipeline",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info(f"Scheduler started — running every {interval_minutes} minutes")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


async def trigger_now() -> None:
    """Manually trigger a scrape (for admin panel)."""
    await run_scrape_pipeline()
