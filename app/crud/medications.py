from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.medications import Medication
from app.schemas.medications import MedicationCreate, MedicationUpdate


async def create_medication(
    db: AsyncSession, patient_id: UUID, doctor_id: UUID, obj_in: MedicationCreate
) -> Medication:
    db_obj = Medication(patient_id=patient_id, doctor_id=doctor_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_medications(
    db: AsyncSession,
    patient_id: UUID,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, List[Medication]]:
    query = select(Medication).where(
        Medication.patient_id == patient_id,
        Medication.deleted_at.is_(None),
    )
    if active is not None:
        query = query.where(Medication.active == active)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (
        await db.execute(query.order_by(Medication.start_date.desc()).offset(skip).limit(limit))
    ).scalars().all()
    return total, list(items)


async def get_medication(db: AsyncSession, medication_id: UUID) -> Optional[Medication]:
    result = await db.execute(
        select(Medication).where(Medication.id == medication_id, Medication.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_medication(
    db: AsyncSession, medication: Medication, obj_in: MedicationUpdate
) -> Medication:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(medication, field, value)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication
