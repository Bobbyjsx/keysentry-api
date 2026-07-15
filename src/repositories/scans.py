from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user_data import ScanHistory

class ScanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_scan(self, user_id: UUID, status: str = "pending", trigger: str = None) -> ScanHistory:
        sources = [{"type": "github", "value": trigger}] if trigger and trigger != "manual" else []
        new_scan = ScanHistory(user_id=user_id, status=status, trigger=trigger, sources=sources)
        self.session.add(new_scan)
        await self.session.commit()
        await self.session.refresh(new_scan)
        return new_scan

    async def update_scan_status(self, scan: ScanHistory, status: str) -> ScanHistory:
        scan.status = status
        self.session.add(scan)
        await self.session.commit()
        return scan

    async def get_scan_by_id(self, scan_id: str) -> ScanHistory | None:
        return await self.session.scalar(select(ScanHistory).where(ScanHistory.id == scan_id))

    async def get_by_user_id(self, user_id: UUID) -> list[ScanHistory]:
        result = await self.session.execute(
            select(ScanHistory).where(ScanHistory.user_id == user_id).order_by(ScanHistory.scan_date.desc())
        )
        return list(result.scalars().all())

    async def get_paginated(self, user_id: UUID, skip: int, limit: int) -> list[ScanHistory]:
        result = await self.session.execute(
            select(ScanHistory).where(ScanHistory.user_id == user_id).order_by(ScanHistory.scan_date.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
