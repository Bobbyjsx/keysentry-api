import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.lib.trigger import TriggerClient, get_trigger_client
from src.lib.webhook import WebhookEngine, WebhookPayload, get_webhook_engine
from src.repositories.scans import ScanRepository
from src.repositories.user_data import UserDataRepository
from src.services.scans import ScanService
from src.services.user_data import UserDataService

router = APIRouter(prefix="/scans", tags=["scans"])


from typing import List, Optional

class ScanRequest(BaseModel):
    target: str


def get_user_data_service(session: AsyncSession = Depends(get_db)) -> UserDataService:
    return UserDataService(UserDataRepository(session))


def get_scan_service(
    session: AsyncSession = Depends(get_db),
    user_service: UserDataService = Depends(get_user_data_service),
    trigger_client: TriggerClient = Depends(get_trigger_client),
) -> ScanService:
    return ScanService(ScanRepository(session), user_service, trigger_client)


@router.post("/trigger", status_code=202)
async def trigger_scan(
    request: ScanRequest,
    current_user_id: UUID = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
):
    """
    Triggers a background GitHub scan using Trigger.dev.
    Returns immediately with a 202 Accepted status and the scan ID.
    """
    return await scan_service.trigger_github_scan(current_user_id, request.target)

@router.get("/history")
async def get_scan_history(
    current_user_id: UUID = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
):
    """
    Returns the scan history for the current user.
    """
    return await scan_service.get_scan_history(current_user_id)

@router.get("/{scan_id}")
async def get_scan_details(
    scan_id: str,
    current_user_id: UUID = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
):
    """
    Returns details for a specific scan.
    """
    return await scan_service.get_scan_details(scan_id)

@router.get("/")
async def list_scans(
    page: int = 1,
    pageSize: int = 20,
    current_user_id: UUID = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
):
    """
    Returns paginated scans.
    """
    return await scan_service.list_scans(current_user_id, page, pageSize)

class ManualScanRequest(BaseModel):
    targetType: str
    targetValue: str

@router.post("/manual")
async def trigger_manual_scan(
    request: ManualScanRequest,
    current_user_id: UUID = Depends(get_current_user),
    scan_service: ScanService = Depends(get_scan_service),
):
    """
    Triggers a manual scan.
    """
    return await scan_service.trigger_github_scan(current_user_id, request.targetValue)


@router.post("/webhook")
async def scan_webhook(
    payload: WebhookPayload,
    request: Request,
    webhook_engine: WebhookEngine = Depends(get_webhook_engine),
):
    from src.core.config import settings

    internal_token = request.headers.get("x-internal-token")
    if (
        not settings.INTERNAL_API_SECRET
        or internal_token != settings.INTERNAL_API_SECRET
    ):
        logging.warning("Unauthorized webhook access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    await webhook_engine.process_scan_webhook(payload)
    return {"status": "success"}

class GitHubWebhookRequest(BaseModel):
    user_id: UUID
    repository: str

@router.post("/github-webhook")
async def github_webhook(
    request: GitHubWebhookRequest,
    req: Request,
    scan_service: ScanService = Depends(get_scan_service),
):
    from src.core.config import settings

    internal_token = req.headers.get("x-internal-token")
    if (
        not settings.INTERNAL_API_SECRET
        or internal_token != settings.INTERNAL_API_SECRET
    ):
        logging.warning("Unauthorized github webhook access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await scan_service.trigger_github_scan(request.user_id, request.repository)
