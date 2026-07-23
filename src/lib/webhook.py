from fastapi import Depends
from src.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.models.user_data import ScanHistory
from src.models.api_key import APIKey


class KeyFoundPayload(BaseModel):
    provider: str = "Unknown"
    key_hash: str = ""
    source: str = ""
    link: str = ""
    repository: str = ""
    risk_level: str = "high"


class WebhookPayload(BaseModel):
    scan_id: str
    user_id: str
    keys_found: List[KeyFoundPayload] = []
    status: str = "succeeded"
    error: Optional[str] = None
    files_scanned: int = 0
    repos_scanned: int = 0
    scanned_repositories: List[str] = []
    attempt: int = 1


class WebhookEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_scan_webhook(self, payload: WebhookPayload) -> None:
        """
        Processes a webhook from the background worker.
        Updates the scan history and adds any discovered API keys.
        """
        # 1. Fetch scan
        scan = await self.db.scalar(
            select(ScanHistory).where(ScanHistory.id == payload.scan_id)
        )
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        import datetime

        now = datetime.datetime.now(datetime.timezone.utc)
        if scan.scan_date:
            # Make scan_date timezone-aware if it isn't
            scan_date_aware = scan.scan_date
            if scan_date_aware.tzinfo is None:
                scan_date_aware = scan_date_aware.replace(tzinfo=datetime.timezone.utc)
            duration = int((now - scan_date_aware).total_seconds())
            scan.duration_seconds = max(0, duration)

        if payload.status == "failed":
            scan.status = "failed"
            scan.error = payload.error
            scan.attempt = payload.attempt
            self.db.add(scan)
            await self.db.commit()

            from src.core.events import event_bus, EventType

            await event_bus.publish(
                EventType.SCAN_FAILED,
                user_id=payload.user_id,
                scan_id=payload.scan_id,
                error=payload.error,
            )
            return

        import uuid

        scan_uuid = (
            uuid.UUID(payload.scan_id)
            if isinstance(payload.scan_id, str)
            else payload.scan_id
        )
        user_uuid = (
            uuid.UUID(payload.user_id)
            if isinstance(payload.user_id, str)
            else payload.user_id
        )

        # 2. Add keys idempotently
        new_keys_added = 0
        for key_data in payload.keys_found:
            existing_key = await self.db.scalar(
                select(APIKey).where(
                    APIKey.scan_id == scan_uuid, APIKey.key_hash == key_data.key_hash
                )
            )
            if existing_key:
                continue

            new_key = APIKey(
                user_id=user_uuid,
                scan_id=scan_uuid,
                provider=key_data.provider,
                key_hash=key_data.key_hash,
                source=key_data.source,
                link=key_data.link,
                repository=key_data.repository,
                risk_level=key_data.risk_level,
            )
            self.db.add(new_key)
            new_keys_added += 1

        # 3. Update status and progress
        scan.status = payload.status
        scan.error = payload.error
        scan.attempt = payload.attempt

        # Accumulate total keys found
        scan.keys_found = scan.keys_found + new_keys_added

        # Accumulate files scanned incrementally
        scan.files_scanned = (scan.files_scanned or 0) + payload.files_scanned  # type: ignore

        if payload.scanned_repositories:
            current_sources = (
                set(scan.sources) if isinstance(scan.sources, list) else set()
            )
            current_sources.update(payload.scanned_repositories)
            scan.sources = list(current_sources)  # type: ignore
            scan.repos_scanned = len(scan.sources)  # type: ignore

        self.db.add(scan)
        await self.db.commit()

        # 4. Emit events for each newly discovered key
        from src.core.events import event_bus, EventType

        if new_keys_added > 0:
            for key_data in payload.keys_found:
                await event_bus.publish(
                    EventType.API_KEY_DISCOVERED,
                    user_id=payload.user_id,
                    provider=key_data.provider,
                    repository=key_data.repository,
                    risk_level=key_data.risk_level,
                )

        # 5. Emit scan completed event only if fully succeeded
        if payload.status == "succeeded":
            await event_bus.publish(
                EventType.SCAN_COMPLETED,
                user_id=payload.user_id,
                scan_id=payload.scan_id,
                keys_found=new_keys_added,
            )


def get_webhook_engine(db: AsyncSession = Depends(get_db)) -> WebhookEngine:
    return WebhookEngine(db)
