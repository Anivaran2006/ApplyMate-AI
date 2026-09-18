"""
ApplyMate AI – API v1 Router
Aggregates all route modules into a single router.
"""

from fastapi import APIRouter

from app.api.v1 import auth, users, subscriptions, notices, bookmarks, notifications, admin, assistant

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subscriptions.router)
api_router.include_router(notices.router)
api_router.include_router(bookmarks.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
api_router.include_router(assistant.router)
