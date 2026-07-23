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
async def test_get_analytics(client: AsyncClient, db_session, auth_headers):
    headers, user_id = auth_headers
    resp = await client.get("/api/v1/analytics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "keys" in data
    assert "scanHistory" in data
