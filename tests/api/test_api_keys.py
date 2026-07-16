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
async def test_api_key_lifecycle(client: AsyncClient, db_session, auth_headers):
    headers, user_id = auth_headers

    # 1. Get empty
    resp = await client.get("/api/v1/discoveries/", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. Add an API key manually to DB
    from src.models.api_key import APIKey

    key_id = str(uuid4())
    key = APIKey(
        id=key_id,
        user_id=user_id,
        key_hash="somehash",
        provider="SomeProvider",
        status="active",
        risk_level="high",
        repository="test-repo",
        source="code",
    )
    db_session.add(key)
    await db_session.commit()

    # 3. Get the key
    resp = await client.get("/api/v1/discoveries/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == key_id

    # 4. Patch status
    resp = await client.patch(
        f"/api/v1/discoveries/{key_id}", json={"status": "revoked"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "revoked"

    # 5. Delete the key
    resp = await client.delete(f"/api/v1/discoveries/{key_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # 6. Verify it's gone
    resp = await client.get("/api/v1/discoveries/", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []
