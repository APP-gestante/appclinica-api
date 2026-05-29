from uuid import UUID
from typing import Optional, List
from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.appointment_evolution import AppointmentEvolution
from app.schemas.appointment_evolution import EvolutionCreate


async def get_evolution(
    db: AsyncSession, appointment_id: UUID
) -> Optional[AppointmentEvolution]:
    result = await db.execute(
        select(AppointmentEvolution).where(
            AppointmentEvolution.appointment_id == appointment_id,
            AppointmentEvolution.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def upsert_evolution(
    db: AsyncSession,
    appointment_id: UUID,
    patient_id: UUID,
    obj_in: EvolutionCreate,
) -> AppointmentEvolution:
    existing = await get_evolution(db, appointment_id)
    if existing:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    evo = AppointmentEvolution(
        appointment_id=appointment_id,
        patient_id=patient_id,
        **obj_in.model_dump(exclude_unset=True),
    )
    db.add(evo)
    await db.commit()
    await db.refresh(evo)
    return evo


async def get_patient_evolutions(
    db: AsyncSession, patient_id: UUID
) -> List[AppointmentEvolution]:
    result = await db.execute(
        select(AppointmentEvolution)
        .where(
            AppointmentEvolution.patient_id == patient_id,
            AppointmentEvolution.deleted_at.is_(None),
        )
        .order_by(asc(AppointmentEvolution.created_at))
    )
    return list(result.scalars().all())
