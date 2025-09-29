"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create test engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_player(test_db: AsyncSession):
    """Create a sample player for testing."""
    from app.models.player import Player

    player = Player(
        name="Test Player",
        email="test@example.com",
        age=25,
        country="USA",
        dominant_hand="right",
        skill_level="advanced"
    )

    test_db.add(player)
    await test_db.commit()
    await test_db.refresh(player)

    return player


@pytest.fixture
async def sample_players(test_db: AsyncSession):
    """Create multiple sample players for testing."""
    from app.models.player import Player

    players = [
        Player(
            name="Player One",
            email="player1@example.com",
            age=24,
            country="USA",
            dominant_hand="right",
            skill_level="professional"
        ),
        Player(
            name="Player Two",
            email="player2@example.com",
            age=26,
            country="ESP",
            dominant_hand="left",
            skill_level="professional"
        )
    ]

    for player in players:
        test_db.add(player)

    await test_db.commit()

    for player in players:
        await test_db.refresh(player)

    return players


@pytest.fixture
async def sample_match(test_db: AsyncSession, sample_players):
    """Create a sample match for testing."""
    from app.models.match import Match

    player1, player2 = sample_players

    match = Match(
        title="Test Match",
        match_type="singles",
        surface="hard",
        player1_id=player1.id,
        player2_id=player2.id,
        tournament_name="Test Tournament",
        venue="Test Court"
    )

    test_db.add(match)
    await test_db.commit()
    await test_db.refresh(match)

    return match