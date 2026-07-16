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


@pytest.mark.asyncio
async def test_alerts_lifecycle(client: AsyncClient, auth_headers):
    headers, user_id = auth_headers

    # 1. Create an alert
    payload = {
        "title": "Test Alert",
        "description": "This is a test alert",
        "severity": "high",
        "user_id": user_id,
    }
    resp = await client.post("/api/v1/alerts", json=payload, headers=headers)
    assert resp.status_code == 200
    alert_id = resp.json()["id"]

    # 2. Get alerts
    resp = await client.get("/api/v1/alerts", headers=headers)
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) >= 1
    assert alerts[0]["title"] == "Test Alert"

    # 3. Get unread count
    resp = await client.get("/api/v1/alerts/unread-count", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1

    # 4. Patch alert status
    resp = await client.patch(
        f"/api/v1/alerts/{alert_id}", json={"is_read": True}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

    # 5. Mark alert read
    resp = await client.post(f"/api/v1/alerts/{alert_id}/read", headers=headers)
    assert resp.status_code == 200

    # 6. Mark all alerts read
    resp = await client.post("/api/v1/alerts/read-all", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
