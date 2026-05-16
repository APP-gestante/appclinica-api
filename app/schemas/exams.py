from typing import Optional, List
from datetime import date
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import UltrasoundType, FetalPresentation

class UltrasoundCreate(CoreModel):
    type: UltrasoundType
    date: date
    ig_weeks: int
    presentation: Optional[FetalPresentation] = None
    placenta_location: Optional[str] = None
    amniotic_fluid_ml: Optional[float] = None
    fetal_heart_rate: Optional[int] = None

class UltrasoundResponse(UltrasoundCreate, BaseEntitySchema):
    patient_id: UUID
    doctor_id: UUID
