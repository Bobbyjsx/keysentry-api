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

    async def trigger_github_scan(self, current_user_id: UUID, target: str) -> dict:
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
                    "repository": target,
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

    async def get_scan_history(self, user_id: UUID) -> list[dict]:
        scans = await self.scan_repo.get_by_user_id(user_id)
        return [
            {
                "id": str(s.id),
                "scanDate": s.scan_date.isoformat(),
                "status": s.status,
                "trigger": s.trigger,
                "triggerLink": s.trigger_link,
                "sourcesScanned": s.sources_scanned,
                "reposScanned": s.repos_scanned,
                "filesScanned": s.files_scanned,
                "durationSeconds": s.duration_seconds,
                "keysFound": s.keys_found,
            }
            for s in scans
        ]

    async def get_scan_details(self, scan_id: str) -> dict:
        scan = await self.scan_repo.get_scan_by_id(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Here we should also get the keys found in this scan, but the schema doesn't link keys to scans directly right now.
        # So we'll just return the scan details.
        return {
            "scan": {
                "id": str(scan.id),
                "scanDate": scan.scan_date.isoformat(),
                "status": scan.status,
                "trigger": scan.trigger,
                "triggerLink": scan.trigger_link,
                "sourcesScanned": scan.sources_scanned,
                "reposScanned": scan.repos_scanned,
                "filesScanned": scan.files_scanned,
                "durationSeconds": scan.duration_seconds,
                "keysFound": scan.keys_found,
            },
            "keys": []
        }

    async def list_scans(self, user_id: UUID, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        scans = await self.scan_repo.get_paginated(user_id, skip, page_size)
        data = [
            {
                "id": str(s.id),
                "scanDate": s.scan_date.isoformat(),
                "status": s.status,
                "trigger": s.trigger,
                "triggerLink": s.trigger_link,
                "sourcesScanned": s.sources_scanned,
                "reposScanned": s.repos_scanned,
                "filesScanned": s.files_scanned,
                "durationSeconds": s.duration_seconds,
                "keysFound": s.keys_found,
            }
            for s in scans
        ]
        return {"data": data, "count": len(data)} # Note: count should ideally be total count
