from sqlalchemy import Column, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.enums import MessageSenderType


class Message(BaseModel):
    __tablename__ = "messages"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sender_role = Column(SQLEnum(MessageSenderType), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
