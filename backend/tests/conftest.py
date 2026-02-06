"""
Pytest configuration and fixtures for MongoDB-based tests
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.core import mongodb as mongodb_module
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def mock_mongodb():
    """Mock MongoDB with mongomock-motor for each test."""
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client[settings.DATABASE_NAME]

    # Patch the global db object
    mongodb_module.db.client = mock_client
    mongodb_module.db.database = mock_db

    yield mock_db

    # Clean up all collections after each test
    for name in await mock_db.list_collection_names():
        await mock_db[name].drop()


@pytest.fixture
async def client(mock_mongodb) -> AsyncGenerator[AsyncClient, None]:
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
