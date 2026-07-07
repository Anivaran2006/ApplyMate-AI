"""
ApplyMate AI – Notification History Routes
"""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.notification_history import NotificationHistory
from app.models.notice import Notice
from app.schemas.notice import NotificationHistoryResponse
from app.services.user_service import get_notification_history

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/history", response_model=List[NotificationHistoryResponse])
async def notification_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's notification history."""
    history = await get_notification_history(db, current_user.id, page, page_size)

    results = []
    for h in history:
        # Fetch notice title
        notice_result = await db.execute(select(Notice).where(Notice.id == h.notice_id))
        notice = notice_result.scalar_one_or_none()
        results.append(NotificationHistoryResponse(
            id=h.id,
            notice_id=h.notice_id,
            notice_title=notice.title if notice else "Unknown Notice",
            channel=h.channel.value,
            status=h.status.value,
            sent_at=h.sent_at,
        ))
    return results
