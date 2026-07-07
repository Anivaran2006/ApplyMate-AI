"""
ApplyMate AI – Admin Service
Business logic for admin dashboard, user management, and analytics.
"""

import csv
import io
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.notice import Notice
from app.models.notification_history import NotificationHistory, NotificationStatus
from app.models.subscription import Subscription
from app.models.user import User
from app.models.log import SystemLog, LogLevel
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_dashboard_stats(db: AsyncSession) -> Dict[str, int]:
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    active_users = (await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )).scalar_one()
    total_notices = (await db.execute(select(func.count()).select_from(Notice))).scalar_one()
    processed = (await db.execute(
        select(func.count()).select_from(Notice).where(Notice.is_processed == True)
    )).scalar_one()
    notifs_sent = (await db.execute(
        select(func.count()).select_from(NotificationHistory)
        .where(NotificationHistory.status == NotificationStatus.SENT)
    )).scalar_one()
    tg_connected = (await db.execute(
        select(func.count()).select_from(User)
        .where(User.telegram_chat_id != None, User.telegram_notifications == True)
    )).scalar_one()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_notices": total_notices,
        "processed_notices": processed,
        "total_notifications_sent": notifs_sent,
        "telegram_connected_users": tg_connected,
    }


async def list_users(
    db: AsyncSession,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
) -> Dict[str, Any]:
    query = select(User)
    count_query = select(func.count()).select_from(User)

    if search:
        like = f"%{search}%"
        query = query.where((User.email.ilike(like)) | (User.full_name.ilike(like)))
        count_query = count_query.where((User.email.ilike(like)) | (User.full_name.ilike(like)))

    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    # Add subscription count per user
    user_data = []
    for u in users:
        sub_count = (await db.execute(
            select(func.count()).select_from(Subscription).where(Subscription.user_id == u.id)
        )).scalar_one()
        user_data.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "telegram_chat_id": u.telegram_chat_id,
            "email_notifications": u.email_notifications,
            "telegram_notifications": u.telegram_notifications,
            "subscription_count": sub_count,
            "created_at": u.created_at,
        })

    return {
        "items": user_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
    }


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    user.is_active = False
    await db.flush()
    return True


async def list_notices(
    db: AsyncSession,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
) -> Dict[str, Any]:
    query = select(Notice)
    count_query = select(func.count()).select_from(Notice)

    if category:
        query = query.where(Notice.category == category)
        count_query = count_query.where(Notice.category == category)

    query = query.order_by(Notice.scraped_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    notices = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    return {
        "items": notices,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
    }


async def get_system_logs(
    db: AsyncSession, page: int = 1, page_size: int = 50
) -> List[SystemLog]:
    result = await db.execute(
        select(SystemLog)
        .order_by(SystemLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all())


async def write_log(
    db: AsyncSession, level: LogLevel, module: str, message: str
) -> None:
    db.add(SystemLog(level=level, module=module, message=message))
    await db.flush()


async def export_users_csv(db: AsyncSession) -> str:
    """Generate a CSV export of all users."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Full Name", "Email", "Active", "Verified",
        "Email Notifications", "Telegram Notifications",
        "Telegram Chat ID", "Created At"
    ])
    for u in users:
        writer.writerow([
            u.id, u.full_name, u.email, u.is_active, u.is_verified,
            u.email_notifications, u.telegram_notifications,
            u.telegram_chat_id or "", u.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    return output.getvalue()
