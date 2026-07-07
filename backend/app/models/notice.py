"""
ApplyMate AI – Notice ORM Model
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bookmark import Bookmark
    from app.models.notification_history import NotificationHistory


class Notice(Base):
    __tablename__ = "notices"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_notice_content_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Source info
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="NTA", nullable=False)  # NTA, etc.
    category: Mapped[str] = mapped_column(String(64), default="GENERAL", nullable=False, index=True)

    # Raw content
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI-generated fields
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_important_dates: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_action_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_eligibility: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_deadline: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # Deduplication
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Status flags
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    notification_history: Mapped[List["NotificationHistory"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Notice id={self.id} category={self.category} title={self.title[:40]!r}>"
