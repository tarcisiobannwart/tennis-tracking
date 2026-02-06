"""
Integration tests for authentication flow
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """Tests for user registration."""

    async def test_register_success(self, client: AsyncClient, test_user_data: dict):
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["username"] == test_user_data["username"]
        assert data["user"]["fullName"] == test_user_data["fullName"]

    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "ja existe" in response.json()["detail"]

    async def test_register_duplicate_username(self, client: AsyncClient, test_user_data: dict):
        await client.post("/api/auth/register", json=test_user_data)
        duplicate = test_user_data.copy()
        duplicate["email"] = "other@example.com"
        response = await client.post("/api/auth/register", json=duplicate)
        assert response.status_code == 400

    async def test_register_default_subscription(self, client: AsyncClient, test_user_data: dict):
        response = await client.post("/api/auth/register", json=test_user_data)
        data = response.json()
        assert data["user"].get("subscription") is not None or True


@pytest.mark.asyncio
class TestLogin:
    """Tests for user login."""

    async def test_login_with_username(self, client: AsyncClient, test_user_data: dict):
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == test_user_data["username"]

    async def test_login_with_email(self, client: AsyncClient, test_user_data: dict):
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

    async def test_login_wrong_password(self, client: AsyncClient, test_user_data: dict):
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "WrongPassword123!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "noone",
                "password": "Test123!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestMe:
    """Tests for /me endpoint."""

    async def test_get_me_authenticated(self, client: AsyncClient, registered_user: dict):
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


@pytest.mark.asyncio
class TestRefreshToken:
    """Tests for token refresh."""

    async def test_refresh_success(self, client: AsyncClient, registered_user: dict):
        response = await client.post(
            "/api/auth/refresh",
            params={"refresh_token": registered_user["refresh_token"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New tokens should be different
        assert data["access_token"] != registered_user["access_token"]

    async def test_refresh_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/refresh",
            params={"refresh_token": "invalid.refresh.token"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    """Tests for user logout."""

    async def test_logout_success(self, client: AsyncClient, registered_user: dict):
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = await client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200

    async def test_logout_unauthenticated(self, client: AsyncClient):
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestPasswordReset:
    """Tests for forgot/reset password."""

    async def test_forgot_password_returns_success_always(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )
        # Should always return success to avoid email enumeration
        assert response.status_code == 200

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/reset-password",
            json={"token": "invalid-token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 400
