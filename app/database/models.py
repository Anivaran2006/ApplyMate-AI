from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


# ================= USER =================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )
    name = Column(
    String,
    default=""
)
    password = Column(
        String,
        nullable=False
    )

    # Keep for compatibility during migration
    category = Column(
        String,
        nullable=False,
        default="GENERAL"
    )

    role = Column(
        String,
        default="student"
    )
    bookmarks = relationship(
    "Bookmark",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    notification_history = relationship(
    "NotificationHistory",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    # ---------- Telegram ----------

    telegram_chat_id = Column(
        String,
        nullable=True
    )

    telegram_link_token = Column(
        String,
        unique=True,
        nullable=True
    )

    # ---------- Notification Preferences ----------

    telegram_notifications = Column(
        Boolean,
        default=True
    )

    email_notifications = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # NEW
    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ================= SUBSCRIPTION =================

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="subscriptions"
    )

# ================= BOOKMARK =================

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    notice_id = Column(
        Integer,
        ForeignKey("notices.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="bookmarks"
    )

    notice = relationship(
        "Notice"
    )

# ================= NOTICE =================

# ================= NOTICE =================

class Notice(Base):
    __tablename__ = "notices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    source = Column(
        String,
        nullable=False
    )

    notice_url = Column(
        String,
        unique=True,
        nullable=False
    )

    # ---------- AI Summary ----------

    summary = Column(
        Text,
        nullable=True
    )

    translated_summary = Column(
        Text,
        nullable=True
    )

    important_dates = Column(
        Text,
        nullable=True
    )

    eligibility = Column(
        Text,
        nullable=True
    )

    action_required = Column(
        Text,
        nullable=True
    )

    keywords = Column(
        Text,
        nullable=True
    )

    # ---------- AI Intelligence ----------

    priority = Column(
        String,
        default="LOW"
    )

    notice_type = Column(
        String,
        default="General"
    )

    deadline = Column(
        String,
        nullable=True
    )

    days_left = Column(
        Integer,
        nullable=True
    )

    is_ai_processed = Column(
        Boolean,
        default=False
    )

    # ---------- Dates ----------

    published_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
# ================= NOTIFICATION HISTORY =================

class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    notice_id = Column(
        Integer,
        ForeignKey("notices.id"),
        nullable=False
    )

    sent_via = Column(
        String,
        nullable=False
    )

    sent_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="notification_history"
    )

    notice = relationship("Notice")
    