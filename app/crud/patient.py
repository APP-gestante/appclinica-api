from uuid import UUID
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.models.user import User, Patient
from app.models.appointments import Appointment
from app.models.enums import AppointmentStatus, RiskLevel
from app.schemas.user import PatientUpdate


async def get_patient(db: AsyncSession, patient_id: UUID) -> Optional[Patient]:
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_patient_with_user(db: AsyncSession, patient_id: UUID) -> Optional[tuple]:
    result = await db.execute(
        select(Patient, User)
        .join(User, Patient.user_id == User.id)
        .where(Patient.id == patient_id, Patient.deleted_at.is_(None))
    )
    return result.one_or_none()


async def update_patient(db: AsyncSession, patient: Patient, obj_in: PatientUpdate) -> Patient:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def get_doctor_patients(
    db: AsyncSession,
    doctor_id: UUID,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, List[tuple]]:
    query = (
        select(Patient, User)
        .join(User, Patient.user_id == User.id)
        .where(Patient.doctor_id == doctor_id, Patient.deleted_at.is_(None))
    )
    if search:
        query = query.where(
            or_(
                User.name.ilike(f"%{search}%"),
                Patient.prontuario.ilike(f"%{search}%"),
            )
        )
    if risk_level:
        query = query.where(Patient.risk_level == risk_level)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    rows = (await db.execute(query.offset(skip).limit(limit).order_by(User.name))).all()
    return total, list(rows)


async def get_doctor_dashboard(db: AsyncSession, doctor_id: UUID) -> dict:
    today = date.today()

    today_count = (await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor_id,
            func.date(Appointment.datetime) == today,
            Appointment.deleted_at.is_(None),
        )
    )).scalar_one()

    active_count = (await db.execute(
        select(func.count(Patient.id)).where(
            Patient.doctor_id == doctor_id,
            Patient.deleted_at.is_(None),
        )
    )).scalar_one()

    return {
        "appointments_today": today_count,
        "active_patients": active_count,
    }


async def get_doctor_agenda_day(db: AsyncSession, doctor_id: UUID, day: date) -> List[Appointment]:
    rows = (await db.execute(
        select(Appointment)
        .options(joinedload(Appointment.patient).joinedload(Patient.user))
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.date == day,
            Appointment.deleted_at.is_(None),
        )
        .order_by(Appointment.time)
    )).scalars().all()
    return list(rows)


async def get_doctor_agenda_week(db: AsyncSession, doctor_id: UUID, start: date) -> List[Appointment]:
    end = start + timedelta(days=6)
    rows = (await db.execute(
        select(Appointment)
        .options(joinedload(Appointment.patient).joinedload(Patient.user))
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.date >= start,
            Appointment.date <= end,
            Appointment.deleted_at.is_(None),
        )
        .order_by(Appointment.date, Appointment.time)
    )).scalars().all()
    return list(rows)


async def get_doctor_upcoming_births(db: AsyncSession, doctor_id: UUID) -> List[tuple]:
    today = date.today()
    horizon = today + timedelta(days=60)
    rows = (await db.execute(
        select(Patient, User)
        .join(User, Patient.user_id == User.id)
        .where(
            Patient.doctor_id == doctor_id,
            Patient.edd >= today,
            Patient.edd <= horizon,
            Patient.deleted_at.is_(None),
        )
        .order_by(Patient.edd)
    )).all()
    return list(rows)


async def get_secretary_dashboard(db: AsyncSession, clinic_id: UUID) -> dict:
    today = date.today()

    today_total = (await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.clinic_id == clinic_id,
            func.date(Appointment.datetime) == today,
            Appointment.deleted_at.is_(None),
        )
    )).scalar_one()

    confirmed_count = (await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.clinic_id == clinic_id,
            func.date(Appointment.datetime) == today,
            Appointment.status == AppointmentStatus.confirmed,
            Appointment.deleted_at.is_(None),
        )
    )).scalar_one()

    total_patients = (await db.execute(
        select(func.count(Patient.id))
        .join(User, Patient.user_id == User.id)
        .where(
            User.clinic_id == clinic_id,
            Patient.deleted_at.is_(None),
        )
    )).scalar_one()

    return {
        "appointments_today": today_total,
        "confirmed": confirmed_count,
        "pending": today_total - confirmed_count,
        "total_patients": total_patients,
    }


async def get_daily_report(db: AsyncSession, clinic_id: UUID, day: date) -> dict:
    base = [
        Appointment.clinic_id == clinic_id,
        func.date(Appointment.datetime) == day,
        Appointment.deleted_at.is_(None),
    ]

    total = (await db.execute(
        select(func.count(Appointment.id)).where(*base)
    )).scalar_one()

    completed = (await db.execute(
        select(func.count(Appointment.id)).where(*base, Appointment.status == AppointmentStatus.completed)
    )).scalar_one()

    cancelled = (await db.execute(
        select(func.count(Appointment.id)).where(*base, Appointment.status == AppointmentStatus.cancelled)
    )).scalar_one()

    new_patients = (await db.execute(
        select(func.count(Patient.id))
        .join(User, Patient.user_id == User.id)
        .where(
            User.clinic_id == clinic_id,
            func.date(Patient.created_at) == day,
            Patient.deleted_at.is_(None),
        )
    )).scalar_one()

    return {
        "date": str(day),
        "total_appointments": total,
        "completed": completed,
        "cancelled": cancelled,
        "no_show": 0,
        "new_patients": new_patients,
    }


async def create_patient_with_user(
    db: AsyncSession,
    name: str,
    email: str,
    phone: Optional[str],
    password_hash: str,
    clinic_id: UUID,
    doctor_id: UUID,
    prontuario: str,
    lmp_date: date,
    edd: date,
) -> tuple[User, Patient]:
    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        clinic_id=clinic_id,
        role="patient",
    )
    db.add(user)
    await db.flush()

    patient = Patient(
        user_id=user.id,
        doctor_id=doctor_id,
        prontuario=prontuario,
        lmp_date=lmp_date,
        edd=edd,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(user)
    await db.refresh(patient)
    return user, patient
