from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.clinic import Clinic
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicWithAdminCreate
from app.core.security import get_password_hash

async def get_clinic(db: AsyncSession, clinic_id: UUID) -> Optional[Clinic]:
    result = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
    return result.scalar_one_or_none()

async def get_clinics(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Clinic]:
    result = await db.execute(select(Clinic).offset(skip).limit(limit))
    return result.scalars().all()

async def create_clinic_with_admin(db: AsyncSession, clinic_in: ClinicWithAdminCreate) -> Clinic:
    # 1. Create the Clinic record
    db_clinic = Clinic(
        name=clinic_in.name,
        logo_url=clinic_in.logo_url,
        primary_color=clinic_in.primary_color,
        secondary_color=clinic_in.secondary_color,
        accent_color=clinic_in.accent_color,
        address=clinic_in.address,
        phone=clinic_in.phone,
        email=clinic_in.email,
        website=clinic_in.website,
        timezone=clinic_in.timezone,
        language=clinic_in.language
    )
    db.add(db_clinic)
    await db.flush()  # To get the ID
    
    # 2. Create the initial Admin user
    db_admin = User(
        email=clinic_in.admin_email,
        password_hash=get_password_hash(clinic_in.admin_password),
        name=clinic_in.admin_name,
        role=UserRole.admin,
        clinic_id=db_clinic.id,
        is_active=True,
        email_verified=True
    )
    db.add(db_admin)
    
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic

async def update_clinic(db: AsyncSession, db_clinic: Clinic, clinic_in: ClinicUpdate) -> Clinic:
    update_data = clinic_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_clinic, field, value)
    
    db.add(db_clinic)
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic
