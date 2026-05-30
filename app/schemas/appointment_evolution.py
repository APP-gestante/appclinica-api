from typing import Optional
from uuid import UUID
from decimal import Decimal
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import FetalPresentation


class EvolutionBase(CoreModel):
    weight_kg: Optional[Decimal] = None
    fundal_height_cm: Optional[Decimal] = None
    fetal_heart_rate: Optional[int] = None
    presentation: Optional[FetalPresentation] = None
    fetal_movements: Optional[bool] = None
    edema: Optional[str] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    clinical_notes: Optional[str] = None

    queixas: Optional[str] = None
    observacoes_medicas: Optional[str] = None
    pfe_gramas: Optional[int] = None
    pfe_percentil: Optional[str] = None
    doppler: Optional[str] = None
    observacoes_exame_fisico: Optional[str] = None
    conduta: Optional[str] = None


class EvolutionCreate(EvolutionBase):
    pass


class EvolutionResponse(EvolutionBase, BaseEntitySchema):
    appointment_id: UUID
    patient_id: UUID
