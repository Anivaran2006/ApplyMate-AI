"""
ApplyMate AI – Subscription Schemas
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.models.subscription import CategoryEnum


class SubscriptionCreate(BaseModel):
    category: CategoryEnum


class SubscriptionResponse(BaseModel):
    id: int
    category: CategoryEnum
    created_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionsListResponse(BaseModel):
    categories: List[str]


class SubscriptionBulkUpdate(BaseModel):
    categories: List[CategoryEnum]
