"""
ApplyMate AI – System Log ORM Model
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<SystemLog level={self.level} module={self.module}>"
