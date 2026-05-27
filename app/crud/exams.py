from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.exams import Ultrasound, Vaccine
from app.schemas.exams import UltrasoundCreate, VaccineCreate, VaccineUpdate


# --- Ultrassom ---

async def create_ultrasound(
    db: AsyncSession, patient_id: UUID, doctor_id: UUID, obj_in: UltrasoundCreate
) -> Ultrasound:
    db_obj = Ultrasound(patient_id=patient_id, doctor_id=doctor_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_ultrasounds(
    db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 20
) -> tuple[int, List[Ultrasound]]:
    query = select(Ultrasound).where(
        Ultrasound.patient_id == patient_id, Ultrasound.deleted_at.is_(None)
    )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (
        await db.execute(query.offset(skip).limit(limit).order_by(Ultrasound.date.desc()))
    ).scalars().all()
    return total, list(items)


# --- Vacinas ---

async def create_vaccine(
    db: AsyncSession, patient_id: UUID, doctor_id: Optional[UUID], obj_in: VaccineCreate
) -> Vaccine:
    db_obj = Vaccine(patient_id=patient_id, doctor_id=doctor_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_vaccines(
    db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50
) -> tuple[int, List[Vaccine]]:
    query = select(Vaccine).where(
        Vaccine.patient_id == patient_id, Vaccine.deleted_at.is_(None)
    )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (
        await db.execute(query.offset(skip).limit(limit).order_by(Vaccine.date.desc()))
    ).scalars().all()
    return total, list(items)


async def get_vaccine(db: AsyncSession, vaccine_id: UUID) -> Optional[Vaccine]:
    result = await db.execute(
        select(Vaccine).where(Vaccine.id == vaccine_id, Vaccine.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_vaccine(db: AsyncSession, vaccine: Vaccine, obj_in: VaccineUpdate) -> Vaccine:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(vaccine, field, value)
    db.add(vaccine)
    await db.commit()
    await db.refresh(vaccine)
    return vaccine
