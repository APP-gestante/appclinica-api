from typing import Optional, List
import datetime as dt
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import UltrasoundType, FetalPresentation

class UltrasoundCreate(CoreModel):
    type: UltrasoundType = Field(..., description="Tipo de ultrassonografia realizada (obstetric, morphology, detailed).", examples=["obstetric"])
    date: dt.date = Field(..., description="Data em que o exame foi realizado.", examples=["2024-02-15"])
    ig_weeks: int = Field(..., description="Idade gestacional calculada em semanas completas na data do exame.", examples=[24])
    presentation: Optional[FetalPresentation] = Field(None, description="Apresentação do feto no útero (cephalic, breech, transverse).", examples=["cephalic"])
    placenta_location: Optional[str] = Field(None, description="Localização anatômica da placenta no útero.", examples=["anterior"])
    amniotic_fluid_ml: Optional[float] = Field(None, description="Volume estimado do líquido amniótico em mililitros (mL).", examples=[850.0])
    fetal_heart_rate: Optional[int] = Field(None, description="Frequência cardíaca fetal registrada durante o exame em bpm.", examples=[150])

class UltrasoundResponse(UltrasoundCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da paciente gestante associada.")
    doctor_id: UUID = Field(..., description="Identificador único (UUID) do médico/obstetra que assinou o laudo.")

class UltrasoundListResponse(CoreModel):
    total: int = Field(..., description="Total de exames.", examples=[3])
    limit: int = Field(..., description="Limite por página.", examples=[20])
    offset: int = Field(..., description="Offset de paginação.", examples=[0])
    data: List[UltrasoundResponse]


# --- Vacinas ---
from app.models.enums import VaccineStatus  # noqa: E402

class VaccineCreate(CoreModel):
    vaccine_type: str = Field(..., description="Nome da vacina (ex: Influenza, Hepatite B).", examples=["Influenza"])
    date: dt.date = Field(..., description="Data de aplicação ou agendamento.", examples=["2024-03-15"])
    dose_number: Optional[int] = Field(None, description="Número da dose.", examples=[1])
    status: VaccineStatus = Field(VaccineStatus.scheduled, description="Status (scheduled, completed, missed).", examples=["completed"])
    reactions: Optional[str] = Field(None, description="Reações adversas observadas.", examples=["Dor local leve"])

class VaccineUpdate(CoreModel):
    status: Optional[VaccineStatus] = Field(None, description="Novo status da vacina.")
    reactions: Optional[str] = Field(None, description="Reações adversas atualizadas.")

class VaccineResponse(VaccineCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="ID da paciente associada.")
    doctor_id: Optional[UUID] = Field(None, description="ID do médico que registrou.")

class VaccineListResponse(CoreModel):
    total: int = Field(..., description="Total de vacinas.", examples=[5])
    limit: int = Field(..., description="Limite por página.", examples=[50])
    offset: int = Field(..., description="Offset de paginação.", examples=[0])
    data: List[VaccineResponse]
