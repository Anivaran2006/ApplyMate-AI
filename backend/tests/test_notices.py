"""
ApplyMate AI – Examination Notice & Bookmark Tests
Verifies notice feeds, search/filtering, bookmarks, and AI actions.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.models.notice import Notice
from app.models.user import User


@pytest.mark.asyncio
async def test_list_notices_public_unauthenticated(client: AsyncClient, test_notice: Notice):
    """Verify unauthenticated public visitors can view the notices feed without 401."""
    response = await client.get("/api/v1/notices")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    first = data["items"][0]
    assert first["title"] == test_notice.title
    assert first["is_bookmarked"] is False


@pytest.mark.asyncio
async def test_list_notices_filter_category(client: AsyncClient, test_notice: Notice):
    """Verify category query parameter filters notices."""
    response = await client.get("/api/v1/notices?category=NEET")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1

    # Non-matching category
    response_empty = await client.get("/api/v1/notices?category=NONEXISTENT")
    assert response_empty.status_code == 200
    assert len(response_empty.json()["items"]) == 0


@pytest.mark.asyncio
async def test_list_notices_search_query(client: AsyncClient, test_notice: Notice):
    """Verify text search query parameter filters notices."""
    response = await client.get("/api/v1/notices?search=Registration")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1


@pytest.mark.asyncio
async def test_get_single_notice(client: AsyncClient, test_notice: Notice):
    """Verify retrieving a notice by its database ID."""
    response = await client.get(f"/api/v1/notices/{test_notice.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_notice.id
    assert data["category"] == "NEET"


@pytest.mark.asyncio
async def test_get_nonexistent_notice(client: AsyncClient):
    """Verify 404 Not Found for non-existent notice ID."""
    response = await client.get("/api/v1/notices/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_bookmark_lifecycle(client: AsyncClient, test_user: User, auth_headers: dict, test_notice: Notice):
    """Verify adding, listing, and removing bookmarks."""
    # 1. Initially empty
    res_init = await client.get("/api/v1/bookmarks", headers=auth_headers)
    assert res_init.status_code == 200
    assert len(res_init.json()) == 0

    # 2. Add bookmark
    res_add = await client.post(f"/api/v1/bookmarks/{test_notice.id}", headers=auth_headers)
    assert res_add.status_code == 201

    # 3. Verify in bookmarks list
    res_list = await client.get("/api/v1/bookmarks", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 4. Verify notice list marks is_bookmarked as True
    res_notices = await client.get("/api/v1/notices", headers=auth_headers)
    assert res_notices.json()["items"][0]["is_bookmarked"] is True

    # 5. Remove bookmark
    res_del = await client.delete(f"/api/v1/bookmarks/{test_notice.id}", headers=auth_headers)
    assert res_del.status_code == 200

    # 6. Verify removed
    res_final = await client.get("/api/v1/bookmarks", headers=auth_headers)
    assert len(res_final.json()) == 0


@pytest.mark.asyncio
@patch("app.api.v1.notices.translate_to_hindi", new_callable=AsyncMock)
async def test_ai_action_translate_hindi(mock_translate, client: AsyncClient, test_user: User, auth_headers: dict, test_notice: Notice):
    """Verify AI translate action calls translation service."""
    mock_translate.return_value = "नीट यूजी 2026 के लिए ऑनलाइन आवेदन शुरू हो गया है।"
    payload = {"action": "translate_hindi"}
    response = await client.post(f"/api/v1/notices/{test_notice.id}/ai-action", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "translate_hindi"
    assert "नीट" in data["result"]

