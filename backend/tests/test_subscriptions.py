"""
ApplyMate AI – Subscription Category Tests
Verifies subscribing, unsubscribing, and bulk updating examination categories.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_list_subscriptions_empty(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify new user starts with empty subscriptions list."""
    response = await client.get("/api/v1/subscriptions", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_add_subscription_success(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify subscribing to NEET category."""
    response = await client.post(
        "/api/v1/subscriptions",
        json={"category": "NEET"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "NEET"
    assert "id" in data


@pytest.mark.asyncio
async def test_add_duplicate_subscription(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify duplicate category subscription returns 409 Conflict."""
    await client.post("/api/v1/subscriptions", json={"category": "JEE"}, headers=auth_headers)
    response = await client.post("/api/v1/subscriptions", json={"category": "JEE"}, headers=auth_headers)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_remove_subscription_success(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify removing an existing subscription."""
    await client.post("/api/v1/subscriptions", json={"category": "GATE"}, headers=auth_headers)
    response = await client.delete("/api/v1/subscriptions/GATE", headers=auth_headers)
    assert response.status_code == 200
    assert "unsubscribed" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_remove_nonexistent_subscription(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify 404 when unsubscribing from a category never added."""
    response = await client.delete("/api/v1/subscriptions/UPSC", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_bulk_update_subscriptions(client: AsyncClient, test_user: User, auth_headers: dict):
    """Verify atomic bulk update of exam subscriptions."""
    payload = {"categories": ["NEET", "JEE", "CUET"]}
    response = await client.put("/api/v1/subscriptions/bulk", json=payload, headers=auth_headers)
    assert response.status_code == 200
    categories = [item["category"] for item in response.json()]
    assert set(categories) == {"NEET", "JEE", "CUET"}
