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
    headers = {"x-internal-token": "test_webhook_secret"}
    resp = await client.post("/api/v1/scans/webhook", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # Fetch API Keys
    from tests.utils import create_test_token
    from src.core.config import settings

    settings.GOTRUE_JWT_SECRET = "testsecret"
    token = create_test_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp2 = await client.get("/api/v1/discoveries", headers=headers)
    assert resp2.status_code == 200
    keys = resp2.json()
    assert len(keys) == 1
    assert keys[0]["provider"] == "OpenAI"


@pytest.fixture
def auth_headers():
    user_id = str(uuid4())
    from src.core.config import settings
    from tests.utils import create_test_token

    settings.GOTRUE_JWT_SECRET = "testsecret"
    token = create_test_token(user_id)
    return {"Authorization": f"Bearer {token}"}, user_id


@pytest.mark.asyncio
async def test_scan_endpoints(client: AsyncClient, db_session, auth_headers):
    headers, user_id = auth_headers

    # Mock the trigger client to avoid external API calls
    from unittest.mock import AsyncMock, patch

    with patch(
        "src.lib.trigger.TriggerClient.trigger_task", new_callable=AsyncMock
    ) as mock_trigger:
        mock_trigger.return_value = {"success": True}

        # Make sure the user has a github token in the DB!
        from src.models.user_data import UserSettings

        user_settings = UserSettings(
            user_id=user_id,
            email_alerts=True,
            scan_frequency="weekly",
            theme="dark",
            github_token="fake_github_token",
        )
        db_session.add(user_settings)
        await db_session.commit()
        await db_session.refresh(user_settings)

        # 1. Trigger Scan
        payload = {"target": "test-repo"}
        resp = await client.post("/api/v1/scans/trigger", json=payload, headers=headers)
        assert resp.status_code == 202
        scan_id = resp.json()["scan_id"]
        assert scan_id is not None

        # 2. Get Scan History
        resp = await client.get("/api/v1/scans/history", headers=headers)
        assert resp.status_code == 200
        history = resp.json()
        assert isinstance(history, list)
        assert len(history) >= 1
        assert history[0]["id"] == scan_id

        # 3. Get Scan Details
        resp = await client.get(f"/api/v1/scans/{scan_id}", headers=headers)
        assert resp.status_code == 200
        details = resp.json()
        assert details["scan"]["id"] == scan_id


@pytest.mark.asyncio
async def test_scan_webhook_accumulation(client: AsyncClient, db_session):
    user_id = str(uuid4())
    scan_id = str(uuid4())

    from src.models.user_data import ScanHistory

    scan = ScanHistory(
        id=scan_id,
        user_id=user_id,
        status="running",
        files_scanned=5,
        repos_scanned=0,
        sources=[],
    )
    db_session.add(scan)
    await db_session.commit()

    payload_1 = {
        "scan_id": scan_id,
        "user_id": user_id,
        "keys_found": [],
        "status": "in_progress",
        "files_scanned": 15,
        "scanned_repositories": ["repo1"],
    }

    payload_2 = {
        "scan_id": scan_id,
        "user_id": user_id,
        "keys_found": [],
        "status": "in_progress",
        "files_scanned": 10,
        "scanned_repositories": ["repo2"],
    }

    headers = {"x-internal-token": "test_webhook_secret"}

    resp1 = await client.post("/api/v1/scans/webhook", json=payload_1, headers=headers)
    assert resp1.status_code == 200

    resp2 = await client.post("/api/v1/scans/webhook", json=payload_2, headers=headers)
    assert resp2.status_code == 200

    # Verify accumulation
    await db_session.refresh(scan)
    # Initial 5 + 15 + 10 = 30
    assert scan.files_scanned == 30  # type: ignore
    # repo1, repo2 = 2 repos
    assert scan.repos_scanned == 2  # type: ignore
    assert len(scan.scanned_repositories) == 2  # type: ignore
    assert "repo1" in scan.scanned_repositories
    assert "repo2" in scan.scanned_repositories
