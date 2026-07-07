"""
ApplyMate AI – User Service
Business logic for profile management, subscriptions, and bookmarks.
"""

from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.subscription import Subscription, CategoryEnum
from app.models.bookmark import Bookmark
from app.models.notice import Notice
from app.models.notification_history import NotificationHistory
from app.notifications.telegram import send_welcome_message
from app.schemas.user import UserUpdate, NotificationSettings
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email
    await db.flush()
    return user


async def change_password(db: AsyncSession, user: User, current_pw: str, new_pw: str) -> bool:
    if not verify_password(current_pw, user.hashed_password):
        return False
    user.hashed_password = hash_password(new_pw)
    await db.flush()
    return True


async def update_notification_settings(
    db: AsyncSession, user: User, settings: NotificationSettings
) -> User:
    if settings.email_notifications is not None:
        user.email_notifications = settings.email_notifications
    if settings.telegram_notifications is not None:
        user.telegram_notifications = settings.telegram_notifications
    if settings.telegram_chat_id is not None:
        user.telegram_chat_id = settings.telegram_chat_id
    await db.flush()
    return user


async def connect_telegram(db: AsyncSession, user: User, chat_id: str) -> bool:
    """Link Telegram chat_id to user account and send welcome message."""
    user.telegram_chat_id = chat_id
    user.telegram_notifications = True
    await db.flush()
    # Send welcome notification
    try:
        await send_welcome_message(chat_id, user.full_name)
    except Exception as e:
        logger.warning(f"Welcome Telegram message failed: {e}")
    return True


# ── Subscriptions ─────────────────────────────────────────────────────────────

async def get_user_subscriptions(db: AsyncSession, user_id: int) -> List[Subscription]:
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return list(result.scalars().all())


async def add_subscription(
    db: AsyncSession, user_id: int, category: CategoryEnum
) -> Optional[Subscription]:
    """Add a category subscription. Returns None if already subscribed."""
    existing = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.category == category,
        )
    )
    if existing.scalar_one_or_none():
        return None

    sub = Subscription(user_id=user_id, category=category)
    db.add(sub)
    await db.flush()
    return sub


async def remove_subscription(db: AsyncSession, user_id: int, category: str) -> bool:
    result = await db.execute(
        delete(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.category == category,
        )
    )
    return result.rowcount > 0


async def bulk_update_subscriptions(
    db: AsyncSession, user_id: int, categories: List[CategoryEnum]
) -> List[Subscription]:
    """Replace all user subscriptions with the provided list."""
    await db.execute(delete(Subscription).where(Subscription.user_id == user_id))
    subs = [Subscription(user_id=user_id, category=cat) for cat in categories]
    db.add_all(subs)
    await db.flush()
    return subs


# ── Bookmarks ─────────────────────────────────────────────────────────────────

async def get_bookmarks(db: AsyncSession, user_id: int) -> List[Notice]:
    result = await db.execute(
        select(Notice)
        .join(Bookmark, Bookmark.notice_id == Notice.id)
        .where(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
    )
    return list(result.scalars().all())


async def add_bookmark(db: AsyncSession, user_id: int, notice_id: int) -> bool:
    existing = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == user_id, Bookmark.notice_id == notice_id
        )
    )
    if existing.scalar_one_or_none():
        return False
    db.add(Bookmark(user_id=user_id, notice_id=notice_id))
    await db.flush()
    return True


async def remove_bookmark(db: AsyncSession, user_id: int, notice_id: int) -> bool:
    result = await db.execute(
        delete(Bookmark).where(
            Bookmark.user_id == user_id, Bookmark.notice_id == notice_id
        )
    )
    return result.rowcount > 0


async def get_bookmarked_notice_ids(db: AsyncSession, user_id: int) -> set:
    result = await db.execute(
        select(Bookmark.notice_id).where(Bookmark.user_id == user_id)
    )
    return set(result.scalars().all())


# ── Notification History ──────────────────────────────────────────────────────

async def get_notification_history(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 20
) -> List[NotificationHistory]:
    result = await db.execute(
        select(NotificationHistory)
        .where(NotificationHistory.user_id == user_id)
        .order_by(NotificationHistory.sent_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all())
