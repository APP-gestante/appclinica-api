from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import Message
from app.models.enums import MessageSenderType


async def create_message(
    db: AsyncSession,
    patient_id: UUID,
    sender_id: UUID,
    sender_role: MessageSenderType,
    content: str,
) -> Message:
    msg = Message(
        patient_id=patient_id,
        sender_id=sender_id,
        sender_role=sender_role,
        content=content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages(
    db: AsyncSession,
    patient_id: UUID,
    limit: int = 30,
    offset: int = 0,
    before_id: Optional[UUID] = None,
) -> Tuple[int, List[Message]]:
    base = select(Message).where(
        Message.patient_id == patient_id,
        Message.deleted_at.is_(None),
    )
    if before_id:
        before_msg = (
            await db.execute(select(Message).where(Message.id == before_id))
        ).scalar_one_or_none()
        if before_msg and before_msg.created_at:
            base = base.where(Message.created_at < before_msg.created_at)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = (
        await db.execute(
            base.order_by(Message.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()

    return total, list(rows)


async def mark_all_read(db: AsyncSession, patient_id: UUID) -> int:
    result = await db.execute(
        update(Message)
        .where(Message.patient_id == patient_id, Message.read == False, Message.deleted_at.is_(None))
        .values(read=True)
        .returning(Message.id)
    )
    await db.commit()
    return len(result.fetchall())
