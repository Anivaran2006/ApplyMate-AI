"""
ApplyMate AI – Notice Service
Handles scrape ingestion, AI processing, and notification dispatch.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini import detect_category, generate_notice_summary
from app.models.notice import Notice
from app.models.notification_history import NotificationHistory, NotificationChannel, NotificationStatus
from app.models.subscription import Subscription
from app.models.user import User
from app.notifications.email import notify_user_email
from app.notifications.telegram import notify_user
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def process_scraped_notices(db: AsyncSession, raw_notices: List[dict]) -> int:
    """
    Ingest a list of scraped notice dicts:
    1. Deduplicate via content_hash
    2. Store new notices
    3. Generate AI summaries
    4. Dispatch notifications

    Returns count of newly processed notices.
    """
    new_count = 0

    for raw in raw_notices:
        content_hash = raw.get("content_hash", "")
        if not content_hash:
            continue

        # Skip duplicates
        exists = await db.execute(
            select(Notice).where(Notice.content_hash == content_hash)
        )
        if exists.scalar_one_or_none():
            continue

        # Detect category
        category = await detect_category(raw.get("title", ""))

        # Create notice
        notice = Notice(
            title=raw["title"],
            url=raw["url"],
            source="NTA",
            category=category,
            raw_content=raw.get("raw_content", ""),
            content_hash=content_hash,
            is_processed=False,
            is_notified=False,
        )
        db.add(notice)
        await db.flush()  # get ID

        # Generate AI summary
        try:
            ai_data = await generate_notice_summary(
                notice.title, notice.raw_content or notice.title
            )
            notice.ai_summary = ai_data.get("summary", "")
            notice.ai_explanation = ai_data.get("explanation", "")
            notice.ai_important_dates = ai_data.get("important_dates", "")
            notice.ai_action_required = ai_data.get("action_required", "")
            notice.ai_eligibility = ai_data.get("eligibility", "")
            notice.ai_deadline = ai_data.get("deadline", "")
            notice.is_processed = True
            notice.processed_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"AI processing failed for notice {notice.id}: {e}")

        await db.flush()

        # Notify subscribed users
        await _dispatch_notifications(db, notice)
        notice.is_notified = True
        new_count += 1

    await db.commit()
    return new_count


async def _dispatch_notifications(db: AsyncSession, notice: Notice) -> None:
    """Send notifications to all users subscribed to this notice's category."""
    # Get users subscribed to this category
    result = await db.execute(
        select(User)
        .join(Subscription, Subscription.user_id == User.id)
        .where(
            Subscription.category == notice.category,
            User.is_active == True,
        )
    )
    users = result.scalars().all()
    logger.info(f"Dispatching notice {notice.id} to {len(users)} users (category={notice.category})")

    notice_dict = {
        "title": notice.title,
        "url": notice.url,
        "category": notice.category,
        "ai_summary": notice.ai_summary,
        "ai_explanation": notice.ai_explanation,
        "ai_important_dates": notice.ai_important_dates,
        "ai_action_required": notice.ai_action_required,
        "ai_deadline": notice.ai_deadline,
    }

    for user in users:
        # Telegram
        if user.telegram_notifications and user.telegram_chat_id:
            success = await notify_user(user.telegram_chat_id, notice_dict)
            db.add(NotificationHistory(
                user_id=user.id,
                notice_id=notice.id,
                channel=NotificationChannel.TELEGRAM,
                status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
            ))

        # Email
        if user.email_notifications:
            success = await notify_user_email(user.email, user.full_name, notice_dict)
            db.add(NotificationHistory(
                user_id=user.id,
                notice_id=notice.id,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
            ))

    await db.flush()


async def get_notices(
    db: AsyncSession,
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Fetch paginated, optionally filtered notices."""
    query = select(Notice).where(Notice.is_processed == True)
    count_query = select(func.count()).select_from(Notice).where(Notice.is_processed == True)

    if category:
        query = query.where(Notice.category == category)
        count_query = count_query.where(Notice.category == category)

    if search:
        search_filter = Notice.title.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    query = query.order_by(Notice.scraped_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    results = await db.execute(query)
    notices = results.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "items": notices,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def get_notice_by_id(db: AsyncSession, notice_id: int) -> Optional[Notice]:
    result = await db.execute(select(Notice).where(Notice.id == notice_id))
    return result.scalar_one_or_none()
