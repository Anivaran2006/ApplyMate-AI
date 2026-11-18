"""
ApplyMate AI – Administrative Operations Tests
Verifies admin authentication, metrics retrieval, user management, and security boundaries.
"""

import pytest
from httpx import AsyncClient

from app.models.admin import Admin
from app.models.user import User


@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, test_admin: Admin):
    """Verify administrator login with valid credentials."""
    payload = {
        "email": test_admin.email,
        "password": "AdminPass123!",
    }
    response = await client.post("/api/v1/admin/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_admin_login_invalid(client: AsyncClient):
    """Verify administrator login rejection with invalid credentials."""
    payload = {
        "email": "wrongadmin@applymate.ai",
        "password": "WrongPassword123!",
    }
    response = await client.post("/api/v1/admin/login", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_stats_authenticated(client: AsyncClient, admin_auth_headers: dict):
    """Verify fetching dashboard statistics as an admin."""
    response = await client.get("/api/v1/admin/stats", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_notices" in data


@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_regular_user(client: AsyncClient, auth_headers: dict):
    """Verify regular user receives 403 Forbidden on administrative endpoints."""
    response = await client.get("/api/v1/admin/stats", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, admin_auth_headers: dict, test_user: User):
    """Verify admin can list registered users with pagination."""
    response = await client.get("/api/v1/admin/users", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "users" in data or "items" in data

