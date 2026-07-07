"""
ApplyMate AI – Notification History ORM Model
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.notice import Notice


class NotificationChannel(str, enum.Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    notice_id: Mapped[int] = mapped_column(ForeignKey("notices.id", ondelete="CASCADE"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notification_history")
    notice: Mapped["Notice"] = relationship(back_populates="notification_history")

    def __repr__(self) -> str:
        return f"<NotificationHistory user={self.user_id} notice={self.notice_id} channel={self.channel}>"
