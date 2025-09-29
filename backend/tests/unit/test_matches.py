"""
Unit tests for match API endpoints
"""

import pytest
from httpx import AsyncClient


class TestMatchAPI:
    """Test cases for match API endpoints"""

    @pytest.mark.asyncio
    async def test_create_match(self, client: AsyncClient, sample_players):
        """Test creating a new match"""
        player1, player2 = sample_players

        match_data = {
            "title": "Test Championship Final",
            "match_type": "singles",
            "surface": "hard",
            "player1_id": player1.id,
            "player2_id": player2.id,
            "tournament_name": "Test Championship",
            "venue": "Center Court"
        }

        response = await client.post("/api/matches/", json=match_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == match_data["title"]
        assert data["player1_id"] == player1.id
        assert data["player2_id"] == player2.id
        assert data["status"] == "scheduled"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_match_same_players(self, client: AsyncClient, sample_players):
        """Test creating a match with same player IDs"""
        player1, _ = sample_players

        match_data = {
            "title": "Invalid Match",
            "player1_id": player1.id,
            "player2_id": player1.id  # Same player
        }

        response = await client.post("/api/matches/", json=match_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_matches(self, client: AsyncClient, sample_match):
        """Test getting list of matches"""
        response = await client.get("/api/matches/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == sample_match.id

    @pytest.mark.asyncio
    async def test_get_match_by_id(self, client: AsyncClient, sample_match):
        """Test getting a match by ID with player details"""
        response = await client.get(f"/api/matches/{sample_match.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_match.id
        assert data["title"] == sample_match.title
        assert "player1" in data
        assert "player2" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_match(self, client: AsyncClient):
        """Test getting a nonexistent match"""
        response = await client.get("/api/matches/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_match(self, client: AsyncClient, sample_match):
        """Test updating a match"""
        update_data = {
            "title": "Updated Match Title",
            "venue": "Updated Venue"
        }

        response = await client.put(f"/api/matches/{sample_match.id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Match Title"
        assert data["venue"] == "Updated Venue"
        assert data["tournament_name"] == sample_match.tournament_name  # Unchanged

    @pytest.mark.asyncio
    async def test_start_match(self, client: AsyncClient, sample_match):
        """Test starting a match"""
        response = await client.post(f"/api/matches/{sample_match.id}/start")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert data["match"]["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_finish_match(self, client: AsyncClient, sample_match):
        """Test finishing a match"""
        # First start the match
        await client.post(f"/api/matches/{sample_match.id}/start")

        # Then finish it
        response = await client.post(f"/api/matches/{sample_match.id}/finish")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert data["match"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_match_stats(self, client: AsyncClient, sample_match):
        """Test getting match statistics"""
        response = await client.get(f"/api/matches/{sample_match.id}/stats")
        assert response.status_code == 200

        data = response.json()
        assert "match_id" in data
        assert data["match_id"] == sample_match.id

    @pytest.mark.asyncio
    async def test_get_match_events(self, client: AsyncClient, sample_match):
        """Test getting match events"""
        response = await client.get(f"/api/matches/{sample_match.id}/events")
        assert response.status_code == 200

        data = response.json()
        assert "match_id" in data
        assert data["match_id"] == sample_match.id
        assert "events" in data
        assert "points" in data
        assert "games" in data
        assert "sets" in data

    @pytest.mark.asyncio
    async def test_filter_matches_by_status(self, client: AsyncClient, sample_match):
        """Test filtering matches by status"""
        response = await client.get("/api/matches/?status=scheduled")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "scheduled"

    @pytest.mark.asyncio
    async def test_filter_matches_by_player(self, client: AsyncClient, sample_match, sample_players):
        """Test filtering matches by player"""
        player1, _ = sample_players

        response = await client.get(f"/api/matches/?player_id={player1.id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert (data[0]["player1_id"] == player1.id or data[0]["player2_id"] == player1.id)

    @pytest.mark.asyncio
    async def test_get_active_matches(self, client: AsyncClient, sample_match):
        """Test getting active matches"""
        # Start the match first
        await client.post(f"/api/matches/{sample_match.id}/start")

        response = await client.get("/api/matches/live/active")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_delete_match(self, client: AsyncClient, sample_match):
        """Test deleting a match"""
        response = await client.delete(f"/api/matches/{sample_match.id}")
        assert response.status_code == 200

        # Verify match is deleted
        response = await client.get(f"/api/matches/{sample_match.id}")
        assert response.status_code == 404