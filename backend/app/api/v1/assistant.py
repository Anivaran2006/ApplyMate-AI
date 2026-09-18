"""
ApplyMate AI – AI Assistant API Route
Provides conversational assistance for students using Gemini and official notices.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notice import Notice
from app.ai.gemini import ask_assistant

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Interact with the ApplyMate AI assistant.
    Uses Gemini AI with stored official notice context, falling back to database search.
    """
    notices = []
    try:
        stmt = (
            select(Notice)
            .order_by(desc(Notice.scraped_at))
            .limit(30)
        )
        result = await db.execute(stmt)
        notices = list(result.scalars().all())
    except Exception:
        pass

    answer = await ask_assistant(
        question=request.question,
        notices=notices,
        history=request.history or [],
    )

    return ChatResponse(answer=answer)
