"""
ApplyMate AI – Subscription ORM Model
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class CategoryEnum(str, enum.Enum):
    NEET = "NEET"
    JEE = "JEE"
    CUET = "CUET"
    GATE = "GATE"
    CAT = "CAT"
    UPSC = "UPSC"
    SSC = "SSC"
    BANKING = "BANKING"
    SCHOLARSHIPS = "SCHOLARSHIPS"
    GENERAL = "GENERAL"


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_user_category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category: Mapped[CategoryEnum] = mapped_column(Enum(CategoryEnum), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription user={self.user_id} category={self.category}>"
