import httpx
from typing import Dict, Any


class TriggerClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.trigger.dev/api/v1/tasks"

    async def trigger_task(self, task_id: str, payload: Dict[str, Any]) -> None:
        """
        Triggers a task on Trigger.dev.
        Raises an exception if the request fails.
        """
        if not self.api_key:
            raise ValueError("TRIGGER_API_KEY is not configured")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/{task_id}/trigger",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"payload": payload},
                timeout=5.0,
            )
            resp.raise_for_status()


def get_trigger_client() -> TriggerClient:
    from src.core.config import settings

    return TriggerClient(api_key=settings.TRIGGER_API_KEY)
