from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    category = Column(String, nullable=False)

    telegram_chat_id = Column(String, nullable=True)

    role = Column(String, default="student")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    category = Column(String, nullable=False)

    source = Column(String, nullable=False)

    notice_url = Column(String, nullable=True)

    # -------- AI Fields --------

    summary = Column(Text, nullable=True)

    important_dates = Column(Text, nullable=True)

    eligibility = Column(Text, nullable=True)

    action_required = Column(Text, nullable=True)

    keywords = Column(Text, nullable=True)

    is_ai_processed = Column(Boolean, default=False)

    # ---------------------------

    published_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )