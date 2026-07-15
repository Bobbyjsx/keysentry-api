from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.repositories.user_data import UserDataRepository
from src.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from src.schemas.user import UserSettingsResponse, UserSettingsUpdate
from src.services.user_data import UserDataService

router = APIRouter(tags=["user_data"])


def get_user_data_service(session: AsyncSession = Depends(get_db)) -> UserDataService:
    repository = UserDataRepository(session)
    return UserDataService(repository)


# --- Alerts ---
@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_in: AlertCreate,
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Create a new alert.
    """
    alert_in.user_id = current_user_id
    return await service.create_alert(alert_in)


@router.get("/alerts", response_model=List[AlertResponse])
async def list_user_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Retrieve alerts for the currently authenticated user.
    """
    return await service.get_user_alerts(current_user_id, skip, limit)


@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    update_in: AlertUpdate,
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Update an alert (e.g., mark as read). Uses row-level lock.
    """
    return await service.update_alert_status(alert_id, update_in)


@router.get("/alerts/unread-count")
async def get_unread_alerts_count(
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Get unread alerts count.
    """
    # Simply count where status == 'unread'
    alerts = await service.get_user_alerts(current_user_id, 0, 1000)
    return {"count": sum(1 for a in alerts if a.status == "unread")}


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Mark alert as read.
    """
    return await service.update_alert_status(alert_id, AlertUpdate(status="read"))


@router.post("/alerts/read-all")
async def mark_all_alerts_read(
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Mark all alerts as read.
    """
    alerts = await service.get_user_alerts(current_user_id, 0, 1000)
    for alert in alerts:
        if alert.status == "unread":
            await service.update_alert_status(alert.id, AlertUpdate(status="read"))
    return {"success": True}


# --- Settings ---
@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Retrieve settings for the currently authenticated user.
    """
    return await service.get_user_settings(user_id)


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    update_in: UserSettingsUpdate,
    user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    """
    Update user settings. Uses row-level lock.
    """
    print("hello", update_in)

    return await service.update_user_settings(user_id, update_in)
