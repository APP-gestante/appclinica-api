from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.exams import UltrasoundCreate, UltrasoundResponse

router = APIRouter()

@router.post("/{patient_id}/ultrasounds", response_model=UltrasoundResponse, status_code=status.HTTP_201_CREATED)
async def create_ultrasound(
    patient_id: UUID,
    obj_in: UltrasoundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar ultrassom (Mock)"""
    return {**obj_in.model_dump(), "id": "123e4567-e89b-12d3-a456-426614174000", "patient_id": patient_id, "doctor_id": current_user.id, "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z"}

@router.get("/{patient_id}/ultrasounds")
async def list_ultrasounds(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar ultrassons (Mock)"""
    return {"total": 0, "data": []}
