import pytest
from httpx import AsyncClient
from uuid import uuid4
from tests.utils import create_test_token


@pytest.fixture
def auth_headers():
    user_id = str(uuid4())
    from src.core.config import settings

    settings.GOTRUE_JWT_SECRET = "testsecret"
    token = create_test_token(user_id)
    return {"Authorization": f"Bearer {token}"}, user_id


@pytest.mark.asyncio
async def test_get_user_settings(client: AsyncClient, auth_headers):
    headers, user_id = auth_headers
    resp = await client.get("/api/v1/settings", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user_id
    assert data["theme"] == "dark"


@pytest.mark.asyncio
async def test_update_user_settings(client: AsyncClient, auth_headers):
    headers, user_id = auth_headers
    payload = {"theme": "light"}
    resp = await client.patch("/api/v1/settings", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["theme"] == "light"
