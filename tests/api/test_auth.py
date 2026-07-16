import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from src.schemas.user import AuthResponse
from uuid import uuid4


@pytest.mark.asyncio
async def test_auth_signup(client: AsyncClient):
    with patch(
        "src.services.auth.AuthService.signup", new_callable=AsyncMock
    ) as mock_signup:
        mock_signup.return_value = AuthResponse(
            access_token="fake_token", refresh_token="fake_refresh", user_id=uuid4()
        )
        payload = {
            "email": "test@example.com",
            "password": "password",
            "full_name": "Test User",
        }
        resp = await client.post("/api/v1/auth/signup", json=payload)
        assert resp.status_code == 200
        assert resp.json()["access_token"] == "fake_token"


@pytest.mark.asyncio
async def test_auth_login(client: AsyncClient):
    with patch(
        "src.services.auth.AuthService.login", new_callable=AsyncMock
    ) as mock_login:
        mock_login.return_value = AuthResponse(
            access_token="fake_token_login",
            refresh_token="fake_refresh_login",
            user_id=uuid4(),
        )
        payload = {"email": "test@example.com", "password": "password"}
        resp = await client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code == 200
        assert resp.json()["access_token"] == "fake_token_login"


@pytest.mark.asyncio
async def test_auth_refresh(client: AsyncClient):
    with patch(
        "src.services.auth.AuthService.refresh", new_callable=AsyncMock
    ) as mock_refresh:
        mock_refresh.return_value = AuthResponse(
            access_token="fake_token_refresh",
            refresh_token="fake_refresh_new",
            user_id=uuid4(),
        )
        payload = {"refresh_token": "old_refresh"}
        resp = await client.post("/api/v1/auth/refresh", json=payload)
        assert resp.status_code == 200
        assert resp.json()["access_token"] == "fake_token_refresh"


@pytest.mark.asyncio
async def test_auth_forgot_password(client: AsyncClient):
    payload = {"email": "test@example.com"}
    resp = await client.post("/api/v1/auth/forgot-password", json=payload)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_auth_reset_password(client: AsyncClient):
    payload = {"token": "some_token", "password": "new_password"}
    resp = await client.post("/api/v1/auth/reset-password", json=payload)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
