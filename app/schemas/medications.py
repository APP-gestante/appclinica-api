from typing import Optional, List
from datetime import date
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema


class MedicationCreate(CoreModel):
    name: str = Field(..., description="Nome do medicamento.")
    dosage: str = Field(..., description="Dosagem (ex: 40mg).")
    frequency: str = Field(..., description="Frequência de uso (ex: 2x ao dia).")
    start_date: date = Field(..., description="Data de início do tratamento.")
    end_date: Optional[date] = Field(None, description="Data de término (null = contínuo).")
    instructions: Optional[str] = Field(None, description="Instruções de uso (ex: tomar longe das refeições).")


class MedicationUpdate(CoreModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    end_date: Optional[date] = None
    instructions: Optional[str] = None
    active: Optional[bool] = None


class MedicationResponse(MedicationCreate, BaseEntitySchema):
    patient_id: UUID
    doctor_id: UUID
    active: bool


class MedicationListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[MedicationResponse]
