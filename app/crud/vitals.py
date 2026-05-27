from uuid import UUID
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update

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
    query = select(Contraction).where(Contraction.patient_id == patient_id, Contraction.deleted_at.is_(None))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(Contraction.created_at.desc()))).scalars().all()
    return total, list(items)

async def get_contractions_stats(db: AsyncSession, patient_id: UUID) -> dict:
    result = await db.execute(
        select(
            func.count(Contraction.id),
            func.avg(Contraction.duration_seconds),
            func.avg(Contraction.interval_minutes),
        ).where(Contraction.patient_id == patient_id, Contraction.deleted_at.is_(None))
    )
    row = result.one()
    return {
        "patient_id": patient_id,
        "total_contractions": row[0] or 0,
        "average_duration_seconds": round(float(row[1]), 1) if row[1] else 0.0,
        "average_interval_minutes": round(float(row[2]), 1) if row[2] else None,
    }

async def delete_contractions_session(db: AsyncSession, patient_id: UUID) -> None:
    today = date.today()
    await db.execute(
        update(Contraction)
        .where(
            Contraction.patient_id == patient_id,
            Contraction.session_date == today,
            Contraction.deleted_at.is_(None),
        )
        .values(deleted_at=datetime.utcnow())
    )
    await db.commit()

# --- Glucose ---
async def create_glucose(db: AsyncSession, patient_id: UUID, obj_in: GlucoseReadingCreate) -> GlucoseReading:
    db_obj = GlucoseReading(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_glucose_readings(db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50) -> tuple[int, List[GlucoseReading]]:
    query = select(GlucoseReading).where(GlucoseReading.patient_id == patient_id, GlucoseReading.deleted_at.is_(None))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(GlucoseReading.created_at.desc()))).scalars().all()
    return total, list(items)

async def get_glucose_stats(db: AsyncSession, patient_id: UUID) -> dict:
    agg = await db.execute(
        select(
            func.count(GlucoseReading.id),
            func.avg(GlucoseReading.value_mg_dl),
            func.min(GlucoseReading.value_mg_dl),
            func.max(GlucoseReading.value_mg_dl),
        ).where(GlucoseReading.patient_id == patient_id, GlucoseReading.deleted_at.is_(None))
    )
    row = agg.one()
    last = (await db.execute(
        select(GlucoseReading)
        .where(GlucoseReading.patient_id == patient_id, GlucoseReading.deleted_at.is_(None))
        .order_by(GlucoseReading.created_at.desc())
        .limit(1)
    )).scalar_one_or_none()
    return {
        "patient_id": patient_id,
        "total_readings": row[0] or 0,
        "average": round(float(row[1]), 1) if row[1] else 0.0,
        "min": float(row[2]) if row[2] else None,
        "max": float(row[3]) if row[3] else None,
        "last_reading": {
            "value_mg_dl": float(last.value_mg_dl),
            "moment": last.moment,
            "classification": last.classification,
            "timestamp": last.created_at,
        } if last else None,
    }

async def get_glucose_chart(db: AsyncSession, patient_id: UUID, days: int = 30) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (await db.execute(
        select(GlucoseReading.created_at, GlucoseReading.value_mg_dl, GlucoseReading.moment)
        .where(
            GlucoseReading.patient_id == patient_id,
            GlucoseReading.deleted_at.is_(None),
            GlucoseReading.created_at >= cutoff,
        )
        .order_by(GlucoseReading.created_at)
    )).all()
    return {
        "data": [{"timestamp": r[0], "value": float(r[1]), "moment": r[2]} for r in rows],
        "normal_limit": 95,
        "hypertension_limit": 126,
    }

# --- Blood Pressure ---
async def create_blood_pressure(db: AsyncSession, patient_id: UUID, obj_in: BloodPressureCreate) -> BloodPressureReading:
    db_obj = BloodPressureReading(patient_id=patient_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_blood_pressure_readings(db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 50) -> tuple[int, List[BloodPressureReading]]:
    query = select(BloodPressureReading).where(BloodPressureReading.patient_id == patient_id, BloodPressureReading.deleted_at.is_(None))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit).order_by(BloodPressureReading.created_at.desc()))).scalars().all()
    return total, list(items)

async def get_blood_pressure_stats(db: AsyncSession, patient_id: UUID) -> dict:
    agg = await db.execute(
        select(
            func.count(BloodPressureReading.id),
            func.avg(BloodPressureReading.systolic),
            func.avg(BloodPressureReading.diastolic),
        ).where(BloodPressureReading.patient_id == patient_id, BloodPressureReading.deleted_at.is_(None))
    )
    row = agg.one()
    last = (await db.execute(
        select(BloodPressureReading)
        .where(BloodPressureReading.patient_id == patient_id, BloodPressureReading.deleted_at.is_(None))
        .order_by(BloodPressureReading.created_at.desc())
        .limit(1)
    )).scalar_one_or_none()
    return {
        "patient_id": patient_id,
        "total_readings": row[0] or 0,
        "average_systolic": round(float(row[1]), 1) if row[1] else 0.0,
        "average_diastolic": round(float(row[2]), 1) if row[2] else 0.0,
        "last_reading": {
            "systolic": last.systolic,
            "diastolic": last.diastolic,
            "classification": last.classification,
            "timestamp": last.created_at,
        } if last else None,
    }

async def get_blood_pressure_chart(db: AsyncSession, patient_id: UUID, days: int = 30) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (await db.execute(
        select(BloodPressureReading.created_at, BloodPressureReading.systolic, BloodPressureReading.diastolic)
        .where(
            BloodPressureReading.patient_id == patient_id,
            BloodPressureReading.deleted_at.is_(None),
            BloodPressureReading.created_at >= cutoff,
        )
        .order_by(BloodPressureReading.created_at)
    )).all()
    return {
        "data": [{"timestamp": r[0], "systolic": r[1], "diastolic": r[2]} for r in rows],
        "hypertension_limit": 140,
        "normal_systolic": 120,
        "normal_diastolic": 80,
    }
