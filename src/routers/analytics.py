import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.repositories.scans import ScanRepository
from src.repositories.api_key import APIKeyRepository

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/")
async def get_analytics(
    current_user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns analytics data.
    """
    scan_repo = ScanRepository(session)
    api_key_repo = APIKeyRepository(session)

    # Note: ideally these should be through a service layer
    scans = await scan_repo.get_by_user_id(current_user_id)
    keys = await api_key_repo.get_by_user_id(current_user_id)

    scan_history = [
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

    keys_data = [
        {
            "id": str(k.id),
            "key_hash": k.key_hash,
            "provider": k.provider,
            "status": k.status,
            "risk_level": k.risk_level,
            "discovered_at": k.discovered_at.isoformat(),
            "source": k.source,
            "link": k.link,
            "repository": k.repository,
            "notes": k.notes,
        }
        for k in keys
    ]

    return {
        "keys": keys_data,
        "scanHistory": scan_history
    }
