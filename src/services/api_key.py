from uuid import UUID
from typing import List
from fastapi import HTTPException

from src.repositories.api_key import APIKeyRepository
from src.schemas.api_key import APIKeyCreate, APIKeyUpdate
from src.models.api_key import APIKey

class APIKeyService:
    def __init__(self, repository: APIKeyRepository):
        self.repository = repository

    async def create_api_key(self, api_key_in: APIKeyCreate) -> APIKey:
        return await self.repository.create(api_key_in)

    async def get_user_api_keys(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[APIKey]:
        return await self.repository.get_by_user_id(user_id, skip, limit)

    async def update_api_key_status(self, api_key_id: UUID, update_in: APIKeyUpdate) -> APIKey:
        """
        Updates the API key. Uses a row-level lock (FOR UPDATE) to prevent
        race conditions when multiple requests try to update the same key's status.
        """
        update_data = update_in.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update.")

        # Get for update to lock the row
        db_key = await self.repository.get_by_id_for_update(api_key_id)
        if not db_key:
            raise HTTPException(status_code=404, detail="API Key not found")

        return await self.repository.update(db_key, update_data)

    async def delete_api_key(self, api_key_id: UUID) -> dict:
        db_key = await self.repository.get_by_id_for_update(api_key_id)
        if not db_key:
            raise HTTPException(status_code=404, detail="API Key not found")
        await self.repository.delete(db_key)
        return {"success": True}
