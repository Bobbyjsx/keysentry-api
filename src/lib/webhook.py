import logging
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

class WebhookEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_scan_webhook(self, payload: WebhookPayload) -> None:
        """
        Processes a webhook from the background worker.
        Updates the scan history and adds any discovered API keys.
        """
        # 1. Fetch scan
        scan = await self.db.scalar(select(ScanHistory).where(ScanHistory.id == payload.scan_id))
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
            
        import datetime
        now = datetime.datetime.utcnow()
        if scan.scan_date:
            scan_date_naive = scan.scan_date.replace(tzinfo=None)
            duration = int((now - scan_date_naive).total_seconds())
            scan.duration_seconds = max(0, duration)
            
        if payload.status == "failed":
            scan.status = "failed"
            self.db.add(scan)
            await self.db.commit()
            
            from src.core.events import event_bus, EventType
            await event_bus.publish(
                EventType.SCAN_FAILED,
                user_id=payload.user_id,
                scan_id=payload.scan_id,
                error=payload.error
            )
            return

        # 2. Add keys
        for key_data in payload.keys_found:
            new_key = APIKey(
                user_id=payload.user_id,
                provider=key_data.provider,
                key_hash=key_data.key_hash,
                source=key_data.source,
                link=key_data.link,
                repository=key_data.repository,
                risk_level=key_data.risk_level
            )
            self.db.add(new_key)
            
        # 3. Update status
        scan.status = "succeeded"
        scan.keys_found = len(payload.keys_found)
        self.db.add(scan)
        await self.db.commit()

        # 4. Emit events for each discovered key
        from src.core.events import event_bus, EventType
        for key_data in payload.keys_found:
            await event_bus.publish(
                EventType.API_KEY_DISCOVERED,
                user_id=payload.user_id,
                provider=key_data.provider,
                repository=key_data.repository,
                risk_level=key_data.risk_level
            )

        # 5. Emit scan completed event
        await event_bus.publish(
            EventType.SCAN_COMPLETED,
            user_id=payload.user_id,
            scan_id=payload.scan_id,
            keys_found=len(payload.keys_found)
        )

from fastapi import Depends
from src.core.database import get_db

def get_webhook_engine(db: AsyncSession = Depends(get_db)) -> WebhookEngine:
    return WebhookEngine(db)
