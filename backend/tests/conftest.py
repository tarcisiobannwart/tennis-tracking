"""
Pytest configuration and fixtures for PostgreSQL-based tests
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_data():
    """Standard test user data for registration."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "fullName": "Test User",
        "password": "TestPassword123!",
        "role": "player",
        "language": "pt-BR",
    }


@pytest.fixture
def admin_user_data():
    """Admin test user data for registration."""
    return {
        "email": "admin@example.com",
        "username": "adminuser",
        "fullName": "Admin User",
        "password": "AdminPassword123!",
        "role": "admin",
        "language": "pt-BR",
    }


@pytest.fixture
async def registered_user(client: AsyncClient, test_user_data: dict):
    """Register a user and return the response data with tokens."""
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
async def auth_headers(registered_user: dict):
    """Return authorization headers for the registered user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
