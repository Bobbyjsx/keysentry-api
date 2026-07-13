from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional

from src.models.api_key import APIKey
from src.schemas.api_key import APIKeyCreate, APIKeyUpdate

class APIKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, api_key_in: APIKeyCreate) -> APIKey:
        db_obj = APIKey(**api_key_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, api_key_id: UUID) -> Optional[APIKey]:
        result = await self.session.execute(
            select(APIKey).where(APIKey.id == api_key_id)
        )
        return result.scalars().first()

    async def get_by_id_for_update(self, api_key_id: UUID) -> Optional[APIKey]:
        """
        Fetches an API key with a row-level lock to prevent race conditions during updates.
        """
        result = await self.session.execute(
            select(APIKey).where(APIKey.id == api_key_id).with_for_update()
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[APIKey]:
        result = await self.session.execute(
            select(APIKey).where(APIKey.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, db_obj: APIKey, update_data: dict) -> APIKey:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
