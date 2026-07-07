"""
ApplyMate AI – Notice Routes
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini import explain_more, re_summarize, translate_to_hindi
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notice import AIActionRequest, AIActionResponse, NoticeListResponse, NoticeResponse
from app.services.notice_service import get_notice_by_id, get_notices
from app.services.user_service import get_bookmarked_notice_ids

router = APIRouter(prefix="/notices", tags=["Notices"])


@router.get("", response_model=NoticeListResponse)
async def list_notices(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in notice title"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated notices, optionally filtered by category or search."""
    result = await get_notices(db, category=category, search=search, page=page, page_size=page_size)
    bookmarked_ids = await get_bookmarked_notice_ids(db, current_user.id)

    items = []
    for notice in result["items"]:
        notice_dict = NoticeResponse.model_validate(notice)
        notice_dict.is_bookmarked = notice.id in bookmarked_ids
        items.append(notice_dict)

    return NoticeListResponse(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get("/{notice_id}", response_model=NoticeResponse)
async def get_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single notice by ID."""
    notice = await get_notice_by_id(db, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    bookmarked_ids = await get_bookmarked_notice_ids(db, current_user.id)
    result = NoticeResponse.model_validate(notice)
    result.is_bookmarked = notice.id in bookmarked_ids
    return result


@router.post("/{notice_id}/ai-action", response_model=AIActionResponse)
async def ai_action(
    notice_id: int,
    data: AIActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Perform an on-demand AI action on a notice.
    Actions: explain_more | translate_hindi | re_summarize
    """
    notice = await get_notice_by_id(db, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    try:
        if data.action == "explain_more":
            result = await explain_more(notice.title, notice.ai_summary or notice.title)
        elif data.action == "translate_hindi":
            text = notice.ai_summary or notice.title
            result = await translate_to_hindi(text)
        elif data.action == "re_summarize":
            result = await re_summarize(notice.title, notice.raw_content or notice.title)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {data.action}. Use: explain_more, translate_hindi, re_summarize",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}",
        )

    return AIActionResponse(action=data.action, result=result)
