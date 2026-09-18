"""
ApplyMate AI – Notice Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, model_validator


class NoticeResponse(BaseModel):
    id: int
    title: str
    url: str
    source: str
    category: str
    ai_summary: Optional[str] = None
    summary: Optional[str] = None
    ai_explanation: Optional[str] = None
    ai_important_dates: Optional[str] = None
    ai_action_required: Optional[str] = None
    ai_eligibility: Optional[str] = None
    ai_deadline: Optional[str] = None
    is_processed: bool
    scraped_at: datetime
    is_bookmarked: bool = False

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def sync_summary(self):
        if not self.summary and self.ai_summary:
            self.summary = self.ai_summary
        elif not self.ai_summary and self.summary:
            self.ai_summary = self.summary
        return self


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
