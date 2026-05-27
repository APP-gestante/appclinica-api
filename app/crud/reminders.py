from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminders import Reminder
from app.schemas.reminders import ReminderCreate


async def create_reminder(
    db: AsyncSession,
    obj_in: ReminderCreate,
    patient_id: UUID,
    created_by: UUID,
) -> Reminder:
    reminder = Reminder(
        patient_id=patient_id,
        created_by=created_by,
        **obj_in.model_dump(),
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def get_reminder(db: AsyncSession, reminder_id: UUID) -> Optional[Reminder]:
    result = await db.execute(
        select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def mark_reminder_sent(db: AsyncSession, reminder: Reminder) -> Reminder:
    reminder.sent_at = datetime.now(timezone.utc)
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder
