from typing import Optional, List
from datetime import date
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import VitalClassification, TimeOfDay, GlucoseMoment

# --- Contrações ---
class ContractionCreate(CoreModel):
    duration_seconds: int
    interval_minutes: Optional[float] = None
    session_date: date

class ContractionResponse(ContractionCreate, BaseEntitySchema):
    patient_id: UUID

class ContractionListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[ContractionResponse]

# --- Glicose ---
class GlucoseReadingCreate(CoreModel):
    value_mg_dl: float
    moment: GlucoseMoment
    classification: VitalClassification
    notes: Optional[str] = None

class GlucoseReadingResponse(GlucoseReadingCreate, BaseEntitySchema):
    patient_id: UUID

class GlucoseListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[GlucoseReadingResponse]

# --- Pressão Arterial ---
class BloodPressureCreate(CoreModel):
    systolic: int
    diastolic: int
    pulse_bpm: Optional[int] = None
    moment: TimeOfDay
    classification: VitalClassification

class BloodPressureResponse(BloodPressureCreate, BaseEntitySchema):
    patient_id: UUID

class BloodPressureListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[BloodPressureResponse]
