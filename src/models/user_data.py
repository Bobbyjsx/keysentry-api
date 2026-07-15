import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    scan_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    keys_found = Column(Integer, default=0, nullable=False)
    sources_scanned = Column(Integer, default=0, nullable=False)
    repos_scanned = Column(Integer, default=0, nullable=False)
    files_scanned = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    status = Column(String, default="in_progress", nullable=False)
    trigger = Column(String, default="manual", nullable=False)
    trigger_link = Column(String)
    sources = Column(JSON, default=list, nullable=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    email_alerts = Column(Boolean, default=True, nullable=False)
    slack_webhook = Column(String)
    github_token = Column(String)
    scan_frequency = Column(String, default="daily", nullable=False)
    theme = Column(String, default="dark", nullable=False)
