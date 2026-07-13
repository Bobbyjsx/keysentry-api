from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.core.database import get_db
from src.repositories.user_data import UserDataRepository
from src.services.user_data import UserDataService
from src.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from src.schemas.user import UserSettingsResponse, UserSettingsUpdate
from src.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["user_data"])

def get_user_data_service(session: AsyncSession = Depends(get_db)) -> UserDataService:
    repository = UserDataRepository(session)
    return UserDataService(repository)

# --- Alerts ---
@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_in: AlertCreate,
    current_user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service)
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
    service: UserDataService = Depends(get_user_data_service)
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
    service: UserDataService = Depends(get_user_data_service)
):
    """
    Update an alert (e.g., mark as read). Uses row-level lock.
    """
    return await service.update_alert_status(alert_id, update_in)

# --- Settings ---
@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service)
):
    """
    Retrieve settings for the currently authenticated user.
    """
    return await service.get_user_settings(user_id)

@router.patch("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    update_in: UserSettingsUpdate,
    user_id: UUID = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service)
):
    """
    Update user settings. Uses row-level lock.
    """
    return await service.update_user_settings(user_id, update_in)
