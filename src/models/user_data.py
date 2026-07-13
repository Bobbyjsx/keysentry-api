import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True)
    updated_at = Column(DateTime(timezone=True))
    username = Column(String, unique=True)
    full_name = Column(String)
    avatar_url = Column(String)
    website = Column(String)

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    scan_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    keys_found = Column(Integer, default=0, nullable=False)
    sources_scanned = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    status = Column(String, default="in_progress", nullable=False)
    
    user = relationship("Profile")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    email_alerts = Column(Boolean, default=True, nullable=False)
    slack_webhook = Column(String)
    github_token = Column(String)
    scan_frequency = Column(String, default="daily", nullable=False)
    theme = Column(String, default="dark", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("Profile")
