from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.user import User, Patient, Doctor, Secretary
from app.models.clinic import Clinic
from app.schemas.user import UserUpdate

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    # selectinload permite trazer as relações se necessário
    result = await db.execute(
        select(User).options(selectinload(User.clinic)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
        
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_clinic_by_id(db: AsyncSession, clinic_id: UUID) -> Optional[Clinic]:
    result = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
    return result.scalar_one_or_none()
