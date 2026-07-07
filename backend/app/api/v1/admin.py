"""
ApplyMate AI – Admin Routes
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.admin import Admin
from app.schemas.admin import AdminLoginRequest, AdminStats, ManualNotifyRequest
from app.services.admin_service import (
    deactivate_user,
    export_users_csv,
    get_dashboard_stats,
    get_system_logs,
    list_notices,
    list_users,
)
from app.services.auth_service import login_admin
from app.scraper.scheduler import trigger_now

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login")
async def admin_login(data: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """Admin login endpoint."""
    tokens = await login_admin(db, data.email, data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )
    return tokens


@router.get("/stats", response_model=AdminStats)
async def dashboard_stats(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    return await get_dashboard_stats(db)


@router.get("/users")
async def admin_list_users(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users with search and pagination."""
    return await list_users(db, search=search, page=page, page_size=page_size)


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_user_endpoint(
    user_id: int,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user account."""
    success = await deactivate_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.commit()
    return {"message": f"User {user_id} deactivated"}


@router.get("/notices")
async def admin_list_notices(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all notices with filters."""
    return await list_notices(db, category=category, page=page, page_size=page_size)


@router.post("/notices/scrape-now", status_code=status.HTTP_202_ACCEPTED)
async def scrape_now(admin: Admin = Depends(get_current_admin)):
    """Manually trigger a scrape pipeline run."""
    import asyncio
    asyncio.create_task(trigger_now())
    return {"message": "Scrape pipeline triggered. Check logs for results."}


@router.get("/logs")
async def system_logs(
    page: int = Query(1, ge=1),
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """View system logs."""
    logs = await get_system_logs(db, page=page)
    return [
        {
            "id": log.id,
            "level": log.level.value,
            "module": log.module,
            "message": log.message,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/export/users")
async def export_users(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Export all users as CSV."""
    csv_data = await export_users_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )
