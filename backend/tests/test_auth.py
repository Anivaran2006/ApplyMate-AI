"""
ApplyMate AI – Authentication & Security Tests
Verifies user registration, login, token management, and recovery.
"""

import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from app.models.user import User


@pytest.mark.asyncio
async def test_user_signup_success(client: AsyncClient):
    """Verify standard user registration with valid credentials."""
    payload = {
        "full_name": "New Aspirant",
        "email": "new.aspirant@example.com",
        "password": "StrongPassword123!",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "new.aspirant@example.com"
    assert data["full_name"] == "New Aspirant"


@pytest.mark.asyncio
async def test_user_signup_duplicate_email(client: AsyncClient, test_user: User):
    """Verify signup fails with 400 or 409 when email is already registered."""
    payload = {
        "full_name": "Duplicate Student",
        "email": test_user.email,
        "password": "AnotherPassword123!",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code in (400, 409)
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_signup_validation_failure(client: AsyncClient):
    """Verify signup rejects short passwords."""
    payload = {
        "full_name": "Short Pwd",
        "email": "short@example.com",
        "password": "short",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient, test_user: User):
    """Verify login with valid credentials returns JWT tokens."""
    payload = {
        "email": test_user.email,
        "password": "Password123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_user_login_incorrect_password(client: AsyncClient, test_user: User):
    """Verify login rejection with wrong password."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_login_nonexistent_email(client: AsyncClient):
    """Verify login rejection with unknown email."""
    payload = {
        "email": "ghost@applymate.ai",
        "password": "Password123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh_flow(client: AsyncClient, test_user: User):
    """Verify exchanging a valid refresh token for a new access token."""
    refresh = create_refresh_token(subject=test_user.id)
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_token_refresh_invalid(client: AsyncClient):
    """Verify token refresh rejects malformed token with 401."""
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.jwt.token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_forgot_password_request(client: AsyncClient, test_user: User):
    """Verify password recovery request returns success response."""
    response = await client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
    assert response.status_code == 200
    assert "if this email is registered" in response.json()["message"].lower()


@pytest.mark.asyncio
def test_password_hashing_and_verification():
    """Verify bcrypt hash generation and validation."""
    pwd = "MySecretPassword2026!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongSecretPassword!", hashed) is False


@pytest.mark.asyncio
def test_jwt_token_utilities():
    """Verify JWT access and refresh token creation and verification."""
    user_id = 42
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    assert verify_access_token(access) == str(user_id)
    assert verify_refresh_token(refresh) == str(user_id)

    # Cross-verification should fail
    assert verify_access_token(refresh) is None
    assert verify_refresh_token(access) is None

    # Tampered token should return None
    assert verify_access_token(access + "tampered") is None
