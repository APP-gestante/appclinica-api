from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.patient_anamnesis import PatientAnamnesis
from app.schemas.patient_anamnesis import AnamnesisCreate


async def get_anamnesis(
    db: AsyncSession, patient_id: UUID
) -> Optional[PatientAnamnesis]:
    result = await db.execute(
        select(PatientAnamnesis).where(
            PatientAnamnesis.patient_id == patient_id,
            PatientAnamnesis.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def upsert_anamnesis(
    db: AsyncSession,
    patient_id: UUID,
    obj_in: AnamnesisCreate,
) -> PatientAnamnesis:
    existing = await get_anamnesis(db, patient_id)
    if existing:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    ana = PatientAnamnesis(
        patient_id=patient_id,
        **obj_in.model_dump(exclude_unset=True),
    )
    db.add(ana)
    await db.commit()
    await db.refresh(ana)
    return ana
