from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.user_data import Profile, UserSettings
from src.schemas.alert import AlertCreate


class UserDataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Alerts ---
    async def create_alert(self, alert_in: AlertCreate) -> Alert:
        db_obj = Alert(**alert_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_alerts_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Alert]:
        result = await self.session.execute(
            select(Alert).where(Alert.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_alert_by_id_for_update(self, alert_id: UUID) -> Optional[Alert]:
        result = await self.session.execute(
            select(Alert).where(Alert.id == alert_id).with_for_update()
        )
        return result.scalars().first()

    async def update_alert(self, db_obj: Alert, update_data: dict) -> Alert:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    # --- User Settings ---
    async def get_settings_by_user(self, user_id: UUID) -> Optional[UserSettings]:
        result = await self.session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalars().first()

    async def get_settings_by_user_for_update(
        self, user_id: UUID
    ) -> Optional[UserSettings]:
        result = await self.session.execute(
            select(UserSettings)
            .where(UserSettings.user_id == user_id)
            .with_for_update()
        )
        return result.scalars().first()

    async def update_settings(
        self, db_obj: UserSettings, update_data: dict
    ) -> UserSettings:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    # --- Profile ---
    async def get_profile_by_user(self, user_id: UUID) -> Optional[Profile]:
        result = await self.session.execute(
            select(Profile).where(Profile.id == user_id)
        )
        return result.scalars().first()
