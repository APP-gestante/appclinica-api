from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notification
from app.schemas.notifications import NotificationCreate


async def create_notification(db: AsyncSession, obj_in: NotificationCreate) -> Notification:
    notification = Notification(**obj_in.model_dump())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_notifications(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> Tuple[int, List[Notification]]:
    base = select(Notification).where(
        Notification.user_id == user_id,
        Notification.deleted_at.is_(None),
    )
    if unread_only:
        base = base.where(Notification.read == False)

    total_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(total_q)).scalar_one()

    rows = (
        await db.execute(
            base.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()

    return total, list(rows)


async def get_notification(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def mark_as_read(db: AsyncSession, notification: Notification) -> Notification:
    notification.read = True
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
