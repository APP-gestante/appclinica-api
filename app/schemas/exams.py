from typing import Optional, List
from datetime import date
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import UltrasoundType, FetalPresentation

class UltrasoundCreate(CoreModel):
    type: UltrasoundType = Field(..., description="Tipo de ultrassonografia realizada (obstetric, morphology, detailed).", examples=["obstetric"])
    date: date = Field(..., description="Data em que o exame foi realizado.", examples=["2024-02-15"])
    ig_weeks: int = Field(..., description="Idade gestacional calculada em semanas completas na data do exame.", examples=[24])
    presentation: Optional[FetalPresentation] = Field(None, description="Apresentação do feto no útero (cephalic, breech, transverse).", examples=["cephalic"])
    placenta_location: Optional[str] = Field(None, description="Localização anatômica da placenta no útero.", examples=["anterior"])
    amniotic_fluid_ml: Optional[float] = Field(None, description="Volume estimado do líquido amniótico em mililitros (mL).", examples=[850.0])
    fetal_heart_rate: Optional[int] = Field(None, description="Frequência cardíaca fetal registrada durante o exame em bpm.", examples=[150])

class UltrasoundResponse(UltrasoundCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da paciente gestante associada.")
    doctor_id: UUID = Field(..., description="Identificador único (UUID) do médico/obstetra que assinou o laudo.")
