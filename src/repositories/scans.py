from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user_data import ScanHistory

class ScanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_scan(self, user_id: UUID, status: str = "pending") -> ScanHistory:
        new_scan = ScanHistory(user_id=user_id, status=status)
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
