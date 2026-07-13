from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from uuid import UUID

from src.core.database import get_db
from src.models.user_data import ScanHistory
from src.schemas.user import UserSettingsResponse
from src.services.user_data import UserDataService
from src.repositories.user_data import UserDataRepository
from src.worker.tasks import run_github_scan
from pydantic import BaseModel

router = APIRouter(prefix="/scans", tags=["scans"])

class ScanRequest(BaseModel):
    user_id: UUID
    repository: str

def get_user_data_service(session: AsyncSession = Depends(get_db)) -> UserDataService:
    return UserDataService(UserDataRepository(session))

@router.post("/trigger", status_code=202)
async def trigger_scan(
    request: ScanRequest,
    session: AsyncSession = Depends(get_db),
    user_service: UserDataService = Depends(get_user_data_service)
):
    """
    Triggers a background GitHub scan using Celery.
    Returns immediately with a 202 Accepted status and the scan ID.
    """
    # 1. Fetch user settings to get the github token
    try:
        settings = await user_service.get_user_settings(request.user_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="User settings not found. Cannot retrieve GitHub token.")
        
    if not settings.github_token:
        raise HTTPException(status_code=400, detail="GitHub token not configured for this user.")

    # 2. Create the pending ScanHistory record
    new_scan = ScanHistory(
        user_id=request.user_id,
        status="pending"
    )
    session.add(new_scan)
    await session.commit()
    await session.refresh(new_scan)

    # 3. Dispatch the Celery background task
    # We pass the string representation of UUIDs because Celery serializers prefer strings
    run_github_scan.delay(
        scan_id_str=str(new_scan.id),
        user_id_str=str(request.user_id),
        github_token=settings.github_token,
        repository=request.repository
    )

    return {
        "message": "Scan triggered successfully and sent to background queue.",
        "scan_id": new_scan.id,
        "status": new_scan.status
    }
