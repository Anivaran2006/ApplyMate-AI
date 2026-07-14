from datetime import datetime

from pydantic import BaseModel


# ================= CREATE =================

class NoticeCreate(BaseModel):

    title: str

    description: str

    category: str

    source: str

    notice_url: str | None = None


# ================= RESPONSE =================

class NoticeResponse(BaseModel):

    id: int

    title: str

    description: str

    category: str

    source: str

    notice_url: str | None = None

    # ---------- AI ----------

    summary: str | None = None

    translated_summary: str | None = None

    important_dates: str | None = None

    eligibility: str | None = None

    action_required: str | None = None

    keywords: str | None = None

    priority: str | None = None

    notice_type: str | None = None

    deadline: str | None = None

    days_left: int | None = None

    is_ai_processed: bool

    # ---------- Dates ----------

    published_date: datetime

    created_at: datetime

    class Config:

        from_attributes = True