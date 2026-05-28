from typing import Optional, Any, List
from uuid import UUID
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import NotificationType


class NotificationCreate(CoreModel):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    data: Optional[Any] = None


class NotificationResponse(BaseEntitySchema):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    read: bool
    data: Optional[Any] = None


class NotificationListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[NotificationResponse]
