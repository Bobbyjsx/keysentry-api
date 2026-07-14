import logging
from uuid import UUID
from fastapi import HTTPException
from src.repositories.scans import ScanRepository
from src.services.user_data import UserDataService
from src.lib.trigger import TriggerClient

class ScanService:
    def __init__(
        self,
        scan_repo: ScanRepository,
        user_service: UserDataService,
        trigger_client: TriggerClient
    ):
        self.scan_repo = scan_repo
        self.user_service = user_service
        self.trigger_client = trigger_client

    async def trigger_github_scan(self, current_user_id: UUID, repository: str) -> dict:
        # 1. Fetch user settings to get the github token
        settings = await self.user_service.get_user_settings(current_user_id)

        if not settings.github_token:
            raise HTTPException(
                status_code=400, detail="GitHub token not configured for this user."
            )

        # 2. Create the pending ScanHistory record
        new_scan = await self.scan_repo.create_scan(current_user_id, status="pending")

        # 3. Dispatch the Trigger.dev background task
        try:
            await self.trigger_client.trigger_task(
                task_id="github-scan",
                payload={
                    "scan_id": str(new_scan.id),
                    "user_id": str(current_user_id),
                    "repository": repository,
                    "encrypted_token": settings.github_token,
                },
            )
        except Exception as e:
            logging.error(
                f"Failed to queue trigger.dev task: {type(e).__name__} - {str(e)}"
            )
            await self.scan_repo.update_scan_status(new_scan, "failed")
            raise HTTPException(
                status_code=503,
                detail="Background task queue is currently unavailable. Please try again later.",
            )

        return {
            "message": "Scan triggered successfully and sent to background queue.",
            "scan_id": str(new_scan.id),
            "status": "pending",
        }
