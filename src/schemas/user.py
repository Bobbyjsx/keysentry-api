from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserSettingsUpdate(BaseModel):
    email_alerts: Optional[bool] = None
    slack_webhook: Optional[str] = None
    github_token: Optional[str] = None
    scan_frequency: Optional[str] = None
    theme: Optional[str] = None

class UserSettingsResponse(BaseModel):
    id: UUID
    user_id: UUID
    email_alerts: bool
    slack_webhook: Optional[str] = None
    github_token: Optional[str] = None
    scan_frequency: str
    theme: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuthSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: UUID
