from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.vitals import Contraction, GlucoseReading, BloodPressureReading
from app.schemas.vitals import ContractionCreate, GlucoseReadingCreate, BloodPressureCreate

# --- Contractions ---
async def create_contraction(db: AsyncSession, patient_id: UUID, obj_in: ContractionCreate) -> Contraction:
    db_obj = Contraction(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_contractions(db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50) -> tuple[int, List[Contraction]]:
    query = select(Contraction).where(Contraction.patient_id == patient_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(Contraction.created_at.desc()))).scalars().all()
    return total, list(items)

# --- Glucose ---
async def create_glucose(db: AsyncSession, patient_id: UUID, obj_in: GlucoseReadingCreate) -> GlucoseReading:
    db_obj = GlucoseReading(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_glucose_readings(db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50) -> tuple[int, List[GlucoseReading]]:
    query = select(GlucoseReading).where(GlucoseReading.patient_id == patient_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(GlucoseReading.created_at.desc()))).scalars().all()
    return total, list(items)

# --- Blood Pressure ---
async def create_blood_pressure(db: AsyncSession, patient_id: UUID, obj_in: BloodPressureCreate) -> BloodPressureReading:
    db_obj = BloodPressureReading(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_blood_pressure_readings(db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50) -> tuple[int, List[BloodPressureReading]]:
    query = select(BloodPressureReading).where(BloodPressureReading.patient_id == patient_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(BloodPressureReading.created_at.desc()))).scalars().all()
    return total, list(items)
