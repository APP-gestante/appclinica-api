from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum as SQLEnum
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
