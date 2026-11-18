"""
ApplyMate AI – Automated Test Configuration & Fixtures
Uses in-memory SQLite with aiosqlite for zero-external-dependency, blazing-fast tests.
"""

import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.admin import Admin
from app.models.notice import Notice
from app.models.user import User
from main import app

# In-memory SQLite async engine for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean in-memory database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client with dependency override for get_db."""
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a standard active user."""
    user = User(
        email="student@applymate.ai",
        full_name="Student Aspirant",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
        email_notifications=True,
        telegram_notifications=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User) -> dict:
    """Return Authorization Bearer header for test_user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_admin(db_session: AsyncSession) -> Admin:
    """Create and return an admin user."""
    admin = Admin(
        email="admin@applymate.ai",
        hashed_password=hash_password("AdminPass123!"),
        is_superadmin=True,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(scope="function")
async def admin_auth_headers(test_admin: Admin) -> dict:
    """Return Authorization Bearer header for test_admin."""
    token = create_access_token(subject=test_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_notice(db_session: AsyncSession) -> Notice:
    """Create and return a sample verified notice."""
    notice = Notice(
        title="National Eligibility cum Entrance Test (UG) 2026 Registration Open",
        url="https://exams.nta.ac.in/NEET/notice-2026.pdf",
        source="NTA",
        category="NEET",
        raw_content="NTA invites online applications for NEET UG 2026. Register on exams.nta.ac.in before March 15.",
        ai_summary="Online submission for NEET UG 2026 opened. Last date is March 15, 2026.",
        ai_important_dates="Application Closes: 15 March 2026",
        ai_eligibility="Class 12 with PCB",
        ai_action_required="Complete registration and submit fee online",
        content_hash="hash_neet_ug_2026_test_sample",
        is_processed=True,
        is_notified=True,
    )
    db_session.add(notice)
    await db_session.commit()
    await db_session.refresh(notice)
    return notice
