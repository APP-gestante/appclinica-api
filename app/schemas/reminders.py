from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import ReminderType


class ReminderCreate(CoreModel):
    type: ReminderType
    message: str
    send_at: datetime


class ReminderResponse(BaseEntitySchema):
    patient_id: UUID
    created_by: Optional[UUID] = None
    type: ReminderType
    message: str
    send_at: datetime
    sent_at: Optional[datetime] = None
