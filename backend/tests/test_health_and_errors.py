"""
ApplyMate AI – Health, Routing & Error Handling Tests
Verifies system health, static route serving, 404s, and validation errors.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Verify system health endpoint returns 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ApplyMate" in data["app"]


@pytest.mark.asyncio
async def test_root_serves_landing_page(client: AsyncClient):
    """Verify GET / serves the complete public landing page index.html."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Never miss the opportunity you've been preparing for." in response.text
    assert "ApplyMate" in response.text


@pytest.mark.asyncio
async def test_ui_routes_serve_html(client: AsyncClient):
    """Verify clean URL navigation routes return corresponding HTML pages."""
    routes = [
        ("/login", "Sign In"),
        ("/signup", "Create your free account"),
        ("/dashboard", "Dashboard"),
        ("/forgot-password", "Password Recovery"),
        ("/reset-password", "Set New Password"),
    ]
    for path, expected_text in routes:
        res = await client.get(path)
        assert res.status_code == 200, f"Route {path} failed with {res.status_code}"
        assert expected_text in res.text, f"Route {path} missing '{expected_text}'"


@pytest.mark.asyncio
async def test_api_404_not_found(client: AsyncClient):
    """Verify non-existent API endpoints return 404."""
    response = await client.get("/api/v1/nonexistent-route-xyz")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validation_error_422(client: AsyncClient):
    """Verify malformed JSON payload returns 422 Unprocessable Entity."""
    response = await client.post("/api/v1/auth/login", json={"invalid_field": "data"})
    assert response.status_code == 422

