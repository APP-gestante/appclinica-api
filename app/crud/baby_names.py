from typing import List, Tuple, Optional, Set
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.baby_names import BabyName, PatientBabyNameFavorite
from app.models.enums import BabyNameGender


async def get_baby_names(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    gender: Optional[BabyNameGender] = None,
    search: Optional[str] = None,
) -> Tuple[int, List[BabyName]]:
    base = select(BabyName).where(BabyName.deleted_at.is_(None))
    if gender:
        base = base.where(BabyName.gender == gender)
    if search:
        base = base.where(BabyName.name.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = (
        await db.execute(
            base.order_by(BabyName.popularity_score.desc().nullslast(), BabyName.name).offset(offset).limit(limit)
        )
    ).scalars().all()

    return total, list(rows)


async def get_favorite_ids(db: AsyncSession, patient_id: UUID) -> Set[UUID]:
    result = await db.execute(
        select(PatientBabyNameFavorite.baby_name_id).where(
            PatientBabyNameFavorite.patient_id == patient_id,
            PatientBabyNameFavorite.deleted_at.is_(None),
        )
    )
    return {row for row in result.scalars().all()}


async def get_favorites(
    db: AsyncSession,
    patient_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[int, List[BabyName]]:
    fav_ids_q = (
        select(PatientBabyNameFavorite.baby_name_id)
        .where(
            PatientBabyNameFavorite.patient_id == patient_id,
            PatientBabyNameFavorite.deleted_at.is_(None),
        )
    )
    base = select(BabyName).where(
        BabyName.id.in_(fav_ids_q),
        BabyName.deleted_at.is_(None),
    )
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = (
        await db.execute(base.order_by(BabyName.name).offset(offset).limit(limit))
    ).scalars().all()

    return total, list(rows)


async def get_favorite(
    db: AsyncSession, patient_id: UUID, baby_name_id: UUID
) -> Optional[PatientBabyNameFavorite]:
    result = await db.execute(
        select(PatientBabyNameFavorite).where(
            PatientBabyNameFavorite.patient_id == patient_id,
            PatientBabyNameFavorite.baby_name_id == baby_name_id,
            PatientBabyNameFavorite.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def add_favorite(
    db: AsyncSession, patient_id: UUID, baby_name_id: UUID
) -> PatientBabyNameFavorite:
    fav = PatientBabyNameFavorite(patient_id=patient_id, baby_name_id=baby_name_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


async def remove_favorite(db: AsyncSession, fav: PatientBabyNameFavorite) -> None:
    from datetime import datetime, timezone
    fav.deleted_at = datetime.now(timezone.utc)
    db.add(fav)
    await db.commit()
