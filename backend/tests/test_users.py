"""
ApplyMate AI – User Profile & Account Settings Tests
Verifies profile retrieval, profile updates, password change, and Telegram integration.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_get_current_user_authenticated(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify fetching authenticated user's own profile."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client: AsyncClient):
    """Verify 401 Unauthorized when accessing profile without token."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify updating user display name."""
    payload = {"full_name": "Updated Name Aspirant"}
    response = await client.put("/api/v1/users/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name Aspirant"


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify successfully changing user password."""
    payload = {
        "current_password": "Password123!",
        "new_password": "BrandNewPassword2026!",
    }
    response = await client.put("/api/v1/users/me/password", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify password change fails if current password does not match."""
    payload = {
        "current_password": "IncorrectPassword123!",
        "new_password": "BrandNewPassword2026!",
    }
    response = await client.put("/api/v1/users/me/password", json=payload, headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_notification_preferences(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify updating email and telegram notification toggles."""
    payload = {
        "email_notifications": False,
        "telegram_notifications": True,
    }
    response = await client.put("/api/v1/users/me/notifications", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email_notifications"] is False
    assert data["telegram_notifications"] is True


@pytest.mark.asyncio
async def test_telegram_connect_and_disconnect(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify connecting and disconnecting Telegram chat ID."""
    # Connect
    response = await client.post(
        "/api/v1/users/me/telegram/connect",
        json={"chat_id": "987654321"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "connected" in response.json()["message"].lower()

    # Disconnect
    response = await client.delete("/api/v1/users/me/telegram", headers=auth_headers)
    assert response.status_code == 200
    assert "disconnected" in response.json()["message"].lower()
