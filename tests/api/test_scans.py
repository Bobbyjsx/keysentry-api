import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.fixture(autouse=True)
def mock_event_bus(monkeypatch):
    from src.core.events import event_bus

    async def mock_publish(*args, **kwargs):
        pass

    monkeypatch.setattr(event_bus, "publish", mock_publish)


@pytest.mark.asyncio
async def test_scan_webhook_success(client: AsyncClient, db_session):
    user_id = str(uuid4())
    scan_id = str(uuid4())

    # Needs a scan history row first!
    from src.models.user_data import ScanHistory

    scan = ScanHistory(id=scan_id, user_id=user_id, status="running")
    db_session.add(scan)
    await db_session.commit()

    payload = {
        "scan_id": scan_id,
        "user_id": user_id,
        "keys_found": [
            {
                "provider": "OpenAI",
                "key_hash": "hash123",
                "source": "code",
                "repository": "test",
            }
        ],
        "status": "succeeded",
        "files_scanned": 10,
        "repos_scanned": 1,
    }
    from unittest.mock import patch

    with patch("src.routers.scans.settings.INTERNAL_API_SECRET", "test_webhook_secret"):
        headers = {"Authorization": "Bearer test_webhook_secret"}
        resp = await client.post("/api/v1/scans/webhook", json=payload, headers=headers)
        assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # Fetch API Keys
    from tests.utils import create_test_token
    from src.core.config import settings

    settings.GOTRUE_JWT_SECRET = "testsecret"
    token = create_test_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp2 = await client.get("/api/v1/discoveries/", headers=headers)
    assert resp2.status_code == 200
    keys = resp2.json()["data"]
    assert len(keys) == 1
    assert keys[0]["provider"] == "OpenAI"
