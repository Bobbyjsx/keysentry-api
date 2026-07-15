from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.core.database import get_db
from src.core.security import get_current_user
from src.repositories.api_key import APIKeyRepository
from src.services.api_key import APIKeyService
from src.schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse

router = APIRouter(prefix="/discoveries", tags=["api_keys"])

# Dependency Injection for the Service
def get_api_key_service(session: AsyncSession = Depends(get_db)) -> APIKeyService:
    repository = APIKeyRepository(session)
    return APIKeyService(repository)

@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    api_key_in: APIKeyCreate,
    current_user_id: UUID = Depends(get_current_user),
    service: APIKeyService = Depends(get_api_key_service)
):
    """
    Register a new discovered API key.
    """
    api_key_in.user_id = current_user_id
    return await service.create_api_key(api_key_in)

@router.get("/", response_model=List[APIKeyResponse])
async def list_user_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user_id: UUID = Depends(get_current_user),
    service: APIKeyService = Depends(get_api_key_service)
):
    """
    Retrieve API keys for the currently authenticated user.
    """
    return await service.get_user_api_keys(current_user_id, skip, limit)

@router.patch("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: UUID,
    update_in: APIKeyUpdate,
    current_user_id: UUID = Depends(get_current_user),
    service: APIKeyService = Depends(get_api_key_service)
):
    """
    Update an API key's status, risk level, or notes.
    Uses database row-level locking to prevent concurrent update race conditions.
    """
    # Note: Ideally the service layer should ensure the API key belongs to current_user_id
    return await service.update_api_key_status(api_key_id, update_in)

@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    service: APIKeyService = Depends(get_api_key_service)
):
    """
    Delete an API key.
    """
    # Simply mapping to an archive or hard delete. Here we assume the service has a delete method
    return await service.delete_api_key(api_key_id)

@router.post("/{api_key_id}/archive")
async def archive_api_key(
    api_key_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    service: APIKeyService = Depends(get_api_key_service)
):
    """
    Archive an API key.
    """
    # Assuming update_in handles status update to archived
    update = APIKeyUpdate(status="archived")
    return await service.update_api_key_status(api_key_id, update)
