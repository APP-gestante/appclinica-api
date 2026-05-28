from typing import Optional, List
import datetime as dt
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import VitalClassification, TimeOfDay, GlucoseMoment

# --- Contrações ---
class ContractionCreate(CoreModel):
    duration_seconds: int = Field(..., description="Duração total da contração uterina medida em segundos.", examples=[45])
    interval_minutes: Optional[float] = Field(None, description="Intervalo de tempo decorrido desde a contração anterior em minutos.", examples=[5.5])
    session_date: dt.date = Field(..., description="Data da sessão em que o monitoramento está ocorrendo.", examples=["2024-02-15"])

class ContractionResponse(ContractionCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da paciente gestante.")

class ContractionListResponse(CoreModel):
    total: int = Field(..., description="Quantidade total de registros localizados.", examples=[12])
    limit: int = Field(..., description="Limite de registros por página.", examples=[50])
    offset: int = Field(..., description="Ponto de partida da paginação (offset).", examples=[0])
    data: List[ContractionResponse] = Field(..., description="Lista contendo os registros de contração encontrados.")

# --- Glicose ---
class GlucoseReadingCreate(CoreModel):
    value_mg_dl: float = Field(..., description="Valor obtido na medição da glicose em miligramas por decilitro (mg/dL).", examples=[95.0])
    moment: GlucoseMoment = Field(..., description="Momento do dia ou estado alimentar em que foi feita a medição (fasting, after_meal, random).", examples=["fasting"])
    classification: VitalClassification = Field(..., description="Classificação clínica da medição (normal, attention, high).", examples=["normal"])
    notes: Optional[str] = Field(None, description="Anotações textuais sobre a alimentação ou aplicação de insulina.", examples=["Após café da manhã."])

class GlucoseReadingResponse(GlucoseReadingCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da paciente gestante.")

class GlucoseListResponse(CoreModel):
    total: int = Field(..., description="Quantidade total de registros localizados.", examples=[15])
    limit: int = Field(..., description="Limite de registros por página.", examples=[50])
    offset: int = Field(..., description="Ponto de partida da paginação (offset).", examples=[0])
    data: List[GlucoseReadingResponse] = Field(..., description="Lista de registros de glicemia.")

# --- Pressão Arterial ---
class BloodPressureCreate(CoreModel):
    systolic: int = Field(..., description="Pressão arterial sistólica (máxima) medida em mmHg.", examples=[120])
    diastolic: int = Field(..., description="Pressão arterial diastólica (mínima) medida em mmHg.", examples=[80])
    pulse_bpm: Optional[int] = Field(None, description="Frequência cardíaca medida em batimentos por minuto (bpm).", examples=[72])
    moment: TimeOfDay = Field(..., description="Período do dia em que a pressão foi aferida (morning, afternoon, evening, night).", examples=["morning"])
    classification: VitalClassification = Field(..., description="Classificação clínica da leitura (normal, attention, high).", examples=["normal"])

class BloodPressureResponse(BloodPressureCreate, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da paciente gestante.")

class BloodPressureListResponse(CoreModel):
    total: int = Field(..., description="Quantidade total de registros localizados.", examples=[10])
    limit: int = Field(..., description="Limite de registros por página.", examples=[50])
    offset: int = Field(..., description="Ponto de partida da paginação (offset).", examples=[0])
    data: List[BloodPressureResponse] = Field(..., description="Lista de registros de pressão arterial.")
