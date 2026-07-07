"""
ApplyMate AI – Bookmark Routes
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notice import NoticeResponse
from app.services.user_service import (
    add_bookmark,
    get_bookmarks,
    remove_bookmark,
)

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.get("", response_model=List[NoticeResponse])
async def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all bookmarked notices."""
    notices = await get_bookmarks(db, current_user.id)
    results = []
    for n in notices:
        r = NoticeResponse.model_validate(n)
        r.is_bookmarked = True
        results.append(r)
    return results


@router.post("/{notice_id}", status_code=status.HTTP_201_CREATED)
async def bookmark_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bookmark a notice."""
    added = await add_bookmark(db, current_user.id, notice_id)
    if not added:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Notice already bookmarked",
        )
    await db.commit()
    return {"message": "Notice bookmarked"}


@router.delete("/{notice_id}", status_code=status.HTTP_200_OK)
async def remove_bookmark_endpoint(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a bookmark."""
    removed = await remove_bookmark(db, current_user.id, notice_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    await db.commit()
    return {"message": "Bookmark removed"}
