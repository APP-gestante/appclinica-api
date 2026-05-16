from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.crud import vitals as crud_vitals
from app.schemas.vitals import (
    ContractionCreate, ContractionResponse, ContractionListResponse,
    GlucoseReadingCreate, GlucoseReadingResponse, GlucoseListResponse,
    BloodPressureCreate, BloodPressureResponse, BloodPressureListResponse
)

router = APIRouter()

# --- Contractions ---
@router.post("/{patient_id}/contractions", response_model=ContractionResponse, status_code=status.HTTP_201_CREATED)
async def create_contraction(
    patient_id: UUID,
    obj_in: ContractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_vitals.create_contraction(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/contractions", response_model=ContractionListResponse)
async def list_contractions(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = await crud_vitals.get_contractions(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/contractions/stats")
async def get_contractions_stats(patient_id: UUID):
    """Estatísticas de contrações (Mock)"""
    return {"patient_id": patient_id, "total_contractions": 12, "average_duration_seconds": 47}

@router.delete("/{patient_id}/contractions/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contraction_session(patient_id: UUID):
    """Limpar sessão de contrações do dia (Mock)"""
    return None

# --- Glucose ---
@router.post("/{patient_id}/glucose-readings", response_model=GlucoseReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_glucose(
    patient_id: UUID,
    obj_in: GlucoseReadingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_vitals.create_glucose(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/glucose-readings", response_model=GlucoseListResponse)
async def list_glucose_readings(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = await crud_vitals.get_glucose_readings(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/glucose-readings/stats")
async def get_glucose_stats(patient_id: UUID):
    """Estatísticas de glicose (Mock)"""
    return {"patient_id": patient_id, "total_readings": 15, "average": 92}

@router.get("/{patient_id}/glucose-readings/chart")
async def get_glucose_chart(patient_id: UUID, days: int = 30):
    """Dados para gráfico de glicose (Mock)"""
    return {"data": [], "normal_limit": 95, "hypertension_limit": 126}

# --- Blood Pressure ---
@router.post("/{patient_id}/blood-pressure", response_model=BloodPressureResponse, status_code=status.HTTP_201_CREATED)
async def create_blood_pressure(
    patient_id: UUID,
    obj_in: BloodPressureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_vitals.create_blood_pressure(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/blood-pressure", response_model=BloodPressureListResponse)
async def list_blood_pressure_readings(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = await crud_vitals.get_blood_pressure_readings(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/blood-pressure/stats")
async def get_blood_pressure_stats(patient_id: UUID):
    """Estatísticas de pressão arterial (Mock)"""
    return {"patient_id": patient_id, "total_readings": 10, "average_systolic": 118, "average_diastolic": 78}

@router.get("/{patient_id}/blood-pressure/chart")
async def get_blood_pressure_chart(patient_id: UUID, days: int = 30):
    """Dados para gráfico duplo de pressão (Mock)"""
    return {"data": [], "hypertension_limit": 140, "normal_systolic": 120, "normal_diastolic": 80}
