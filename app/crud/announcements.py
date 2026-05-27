from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.announcements import Announcement
from app.models.enums import AnnouncementCategory
from app.schemas.announcements import AnnouncementCreate

_NEW_THRESHOLD_DAYS = 7


async def create_announcement(
    db: AsyncSession, clinic_id: UUID, obj_in: AnnouncementCreate
) -> dict:
    db_obj = Announcement(clinic_id=clinic_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return _to_dict(db_obj)


async def get_announcements(
    db: AsyncSession,
    clinic_id: UUID,
    category: Optional[AnnouncementCategory] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, List[dict]]:
    now = datetime.utcnow()
    query = select(Announcement).where(
        Announcement.clinic_id == clinic_id,
        Announcement.deleted_at.is_(None),
        (Announcement.expires_at.is_(None)) | (Announcement.expires_at > now),
    )
    if category:
        query = query.where(Announcement.category == category)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (
        await db.execute(query.order_by(Announcement.created_at.desc()).offset(skip).limit(limit))
    ).scalars().all()
    return total, [_to_dict(a) for a in items]


def _to_dict(a: Announcement) -> dict:
    threshold = datetime.utcnow() - timedelta(days=_NEW_THRESHOLD_DAYS)
    return {
        "id": a.id,
        "clinic_id": a.clinic_id,
        "category": a.category,
        "title": a.title,
        "short_description": a.short_description,
        "full_description": a.full_description,
        "expires_at": a.expires_at,
        "is_new": a.created_at >= threshold if a.created_at else False,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
        "deleted_at": a.deleted_at,
    }
