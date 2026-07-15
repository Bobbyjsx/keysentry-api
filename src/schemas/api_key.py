from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class APIKeyBase(BaseModel):
    key_hash: str
    provider: str
    source: str
    link: Optional[str] = None
    repository: Optional[str] = None
    status: str = "active"
    is_archived: bool = False
    risk_level: str = "high"
    notes: Optional[str] = None


class APIKeyCreate(APIKeyBase):
    user_id: UUID


class APIKeyUpdate(BaseModel):
    status: Optional[str] = None
    is_archived: Optional[bool] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class APIKeyResponse(APIKeyBase):
    id: UUID
    user_id: UUID
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
