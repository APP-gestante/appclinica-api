from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.lab_tests import LabTest
from app.models.enums import LabTestType
from app.schemas.lab_tests import LabTestCreate, LabTestUpdate


async def create_lab_test(
    db: AsyncSession, patient_id: UUID, doctor_id: UUID, obj_in: LabTestCreate
) -> LabTest:
    db_obj = LabTest(patient_id=patient_id, doctor_id=doctor_id, **obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_lab_tests(
    db: AsyncSession,
    patient_id: UUID,
    type: Optional[LabTestType] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, List[LabTest]]:
    query = select(LabTest).where(
        LabTest.patient_id == patient_id,
        LabTest.deleted_at.is_(None),
    )
    if type:
        query = query.where(LabTest.type == type)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (
        await db.execute(query.order_by(LabTest.date.desc()).offset(skip).limit(limit))
    ).scalars().all()
    return total, list(items)


async def get_lab_test(db: AsyncSession, lab_test_id: UUID) -> Optional[LabTest]:
    result = await db.execute(
        select(LabTest).where(LabTest.id == lab_test_id, LabTest.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_lab_test(
    db: AsyncSession, lab_test: LabTest, obj_in: LabTestUpdate
) -> LabTest:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(lab_test, field, value)
    db.add(lab_test)
    await db.commit()
    await db.refresh(lab_test)
    return lab_test
