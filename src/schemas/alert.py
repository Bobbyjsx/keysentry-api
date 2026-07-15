from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AlertBase(BaseModel):
    title: str
    description: str
    severity: str
    is_read: bool = False


class AlertCreate(AlertBase):
    user_id: UUID
    api_key_id: Optional[UUID] = None


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None


class AlertResponse(AlertBase):
    id: UUID
    user_id: UUID
    api_key_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
