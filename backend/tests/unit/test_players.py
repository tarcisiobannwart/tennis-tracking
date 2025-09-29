"""
Unit tests for player API endpoints
"""

import pytest
from httpx import AsyncClient


class TestPlayerAPI:
    """Test cases for player API endpoints"""

    @pytest.mark.asyncio
    async def test_create_player(self, client: AsyncClient):
        """Test creating a new player"""
        player_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 25,
            "country": "USA",
            "dominant_hand": "right",
            "skill_level": "intermediate"
        }

        response = await client.post("/api/players/", json=player_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == player_data["name"]
        assert data["email"] == player_data["email"]
        assert data["age"] == player_data["age"]
        assert "id" in data
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_player_invalid_email(self, client: AsyncClient):
        """Test creating a player with invalid email"""
        player_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "age": 25
        }

        response = await client.post("/api/players/", json=player_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_player_invalid_skill_level(self, client: AsyncClient):
        """Test creating a player with invalid skill level"""
        player_data = {
            "name": "John Doe",
            "skill_level": "invalid_level"
        }

        response = await client.post("/api/players/", json=player_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_players(self, client: AsyncClient, sample_players):
        """Test getting list of players"""
        response = await client.get("/api/players/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] in ["Player One", "Player Two"]

    @pytest.mark.asyncio
    async def test_get_player_by_id(self, client: AsyncClient, sample_player):
        """Test getting a player by ID"""
        response = await client.get(f"/api/players/{sample_player.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_player.id
        assert data["name"] == sample_player.name
        assert data["email"] == sample_player.email

    @pytest.mark.asyncio
    async def test_get_nonexistent_player(self, client: AsyncClient):
        """Test getting a nonexistent player"""
        response = await client.get("/api/players/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_player(self, client: AsyncClient, sample_player):
        """Test updating a player"""
        update_data = {
            "name": "Updated Name",
            "age": 30
        }

        response = await client.put(f"/api/players/{sample_player.id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["age"] == 30
        assert data["email"] == sample_player.email  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_player(self, client: AsyncClient, sample_player):
        """Test deleting a player (soft delete)"""
        response = await client.delete(f"/api/players/{sample_player.id}")
        assert response.status_code == 200

        # Verify player is marked as inactive
        response = await client.get(f"/api/players/{sample_player.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_search_players(self, client: AsyncClient, sample_players):
        """Test searching players by name"""
        response = await client.get("/api/players/?search=Player One")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Player One"

    @pytest.mark.asyncio
    async def test_filter_players_by_country(self, client: AsyncClient, sample_players):
        """Test filtering players by country"""
        response = await client.get("/api/players/?country=USA")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["country"] == "USA"

    @pytest.mark.asyncio
    async def test_filter_players_by_skill_level(self, client: AsyncClient, sample_players):
        """Test filtering players by skill level"""
        response = await client.get("/api/players/?skill_level=professional")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        for player in data:
            assert player["skill_level"] == "professional"

    @pytest.mark.asyncio
    async def test_player_pagination(self, client: AsyncClient, sample_players):
        """Test player list pagination"""
        response = await client.get("/api/players/?skip=0&limit=1")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1

        response = await client.get("/api/players/?skip=1&limit=1")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1