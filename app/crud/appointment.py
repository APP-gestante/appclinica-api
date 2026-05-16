from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.appointments import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.models.enums import AppointmentStatus, PatientAppointmentStatus

async def create_appointment(
    db: AsyncSession, doctor_id: UUID, clinic_id: UUID, obj_in: AppointmentCreate
) -> Appointment:
    db_obj = Appointment(
        patient_id=obj_in.patient_id,
        doctor_id=doctor_id,
        clinic_id=clinic_id,
        date=obj_in.date,
        time=obj_in.time,
        datetime=datetime.combine(obj_in.date, obj_in.time),
        duration_minutes=obj_in.duration_minutes,
        type=obj_in.type,
        location=obj_in.location,
        notes=obj_in.notes
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_appointment(db: AsyncSession, appointment_id: UUID) -> Optional[Appointment]:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one_or_none()

async def get_patient_appointments(
    db: AsyncSession, patient_id: UUID, skip: int = 0, limit: int = 20, status: Optional[str] = None
) -> tuple[int, List[Appointment]]:
    query = select(Appointment).where(Appointment.patient_id == patient_id)
    if status:
        query = query.where(Appointment.status == status)
        
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Get items
    query = query.offset(skip).limit(limit).order_by(Appointment.datetime.desc())
    result = await db.execute(query)
    items = result.scalars().all()
    
    return total, list(items)

async def update_appointment(
    db: AsyncSession, db_obj: Appointment, obj_in: dict
) -> Appointment:
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
