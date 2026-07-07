"""
ApplyMate AI – Notice Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class NoticeResponse(BaseModel):
    id: int
    title: str
    url: str
    source: str
    category: str
    ai_summary: Optional[str]
    ai_explanation: Optional[str]
    ai_important_dates: Optional[str]
    ai_action_required: Optional[str]
    ai_eligibility: Optional[str]
    ai_deadline: Optional[str]
    is_processed: bool
    scraped_at: datetime
    is_bookmarked: bool = False

    model_config = {"from_attributes": True}


class NoticeListResponse(BaseModel):
    items: List[NoticeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AIActionRequest(BaseModel):
    action: str  # "explain_more" | "translate_hindi" | "re_summarize"


class AIActionResponse(BaseModel):
    action: str
    result: str


class NotificationHistoryResponse(BaseModel):
    id: int
    notice_id: int
    notice_title: str
    channel: str
    status: str
    sent_at: datetime

    model_config = {"from_attributes": True}
