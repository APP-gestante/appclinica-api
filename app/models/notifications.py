from sqlalchemy import Column, Boolean, Text, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.models.base import BaseModel
from app.models.enums import NotificationType


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    data = Column(JSON, nullable=True)
