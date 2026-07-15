import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scan_history.id", ondelete="SET NULL"), nullable=True)
    key_hash = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    discovered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String, default="active", nullable=False)
    source = Column(String, nullable=False)
    link = Column(String)
    repository = Column(String)
    is_archived = Column(Boolean, default=False, nullable=False)
    risk_level = Column(String, default="high", nullable=False)
    notes = Column(String)

    user = relationship("Profile")

