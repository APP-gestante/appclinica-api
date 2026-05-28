from typing import Optional, List
from uuid import UUID
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import MessageSenderType


class MessageCreate(CoreModel):
    content: str


class MessageResponse(BaseEntitySchema):
    patient_id: UUID
    sender_id: UUID
    sender_role: MessageSenderType
    content: str
    read: bool


class MessageListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[MessageResponse]
