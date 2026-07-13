from uuid import UUID
from typing import List
from fastapi import HTTPException

from src.repositories.user_data import UserDataRepository
from src.schemas.alert import AlertCreate, AlertUpdate
from src.models.alert import Alert
from src.schemas.user import UserSettingsUpdate
from src.models.user_data import UserSettings, Profile

class UserDataService:
    def __init__(self, repository: UserDataRepository):
        self.repository = repository

    async def create_alert(self, alert_in: AlertCreate) -> Alert:
        return await self.repository.create_alert(alert_in)

    async def get_user_alerts(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Alert]:
        return await self.repository.get_alerts_by_user(user_id, skip, limit)

    async def update_alert_status(self, alert_id: UUID, update_in: AlertUpdate) -> Alert:
        update_data = update_in.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update.")

        db_alert = await self.repository.get_alert_by_id_for_update(alert_id)
        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return await self.repository.update_alert(db_alert, update_data)

    async def get_user_settings(self, user_id: UUID) -> UserSettings:
        settings = await self.repository.get_settings_by_user(user_id)
        if not settings:
            raise HTTPException(status_code=404, detail="User settings not found")
        return settings

    async def update_user_settings(self, user_id: UUID, update_in: UserSettingsUpdate) -> UserSettings:
        update_data = update_in.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update.")

        db_settings = await self.repository.get_settings_by_user_for_update(user_id)
        if not db_settings:
            raise HTTPException(status_code=404, detail="User settings not found")

        return await self.repository.update_settings(db_settings, update_data)
