import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logger_middleware(client: AsyncClient):
    # Make a simple request to health check
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    # Make a request that 404s
    resp = await client.get("/invalid_route")
    assert resp.status_code == 404
