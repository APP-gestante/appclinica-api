from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import AnnouncementCategory


class Announcement(BaseModel):
    __tablename__ = "announcements"

    clinic_id = Column(ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False)
    category = Column(SQLEnum(AnnouncementCategory), nullable=False)
    title = Column(String(255), nullable=False)
    short_description = Column(String(500), nullable=False)
    full_description = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    clinic = relationship("Clinic")


class UserAnnouncementRead(BaseModel):
    __tablename__ = "user_announcement_reads"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False)
    read_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "announcement_id", name="uq_user_announcement_read"),
    )
