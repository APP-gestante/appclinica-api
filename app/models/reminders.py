from sqlalchemy import Column, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.enums import ReminderType


class Reminder(BaseModel):
    __tablename__ = "reminders"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    type = Column(SQLEnum(ReminderType), nullable=False)
    message = Column(Text, nullable=False)
    send_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
