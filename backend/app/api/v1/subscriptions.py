"""
ApplyMate AI – Subscription Routes
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionBulkUpdate,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionsListResponse,
)
from app.services.user_service import (
    add_subscription,
    bulk_update_subscriptions,
    get_user_subscriptions,
    remove_subscription,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all active category subscriptions."""
    return await get_user_subscriptions(db, current_user.id)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to a new category."""
    sub = await add_subscription(db, current_user.id, data.category)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already subscribed to this category",
        )
    await db.commit()
    return sub


@router.delete("/{category}", status_code=status.HTTP_200_OK)
async def unsubscribe(
    category: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsubscribe from a category."""
    removed = await remove_subscription(db, current_user.id, category.upper())
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    await db.commit()
    return {"message": f"Unsubscribed from {category.upper()}"}


@router.put("/bulk", response_model=List[SubscriptionResponse])
async def bulk_update(
    data: SubscriptionBulkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace all subscriptions with the provided category list."""
    subs = await bulk_update_subscriptions(db, current_user.id, data.categories)
    await db.commit()
    return subs
