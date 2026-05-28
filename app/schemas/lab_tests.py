from typing import Optional, List
import datetime as dt
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import LabTestType, LabTestStatus


class LabTestCreate(CoreModel):
    type: LabTestType = Field(..., description="Tipo do exame.")
    name: str = Field(..., description="Nome do exame (ex: Hemograma Completo).")
    date: dt.date = Field(..., description="Data de coleta ou realização.")
    result: Optional[str] = Field(None, description="Resultado do exame.")
    reference_range: Optional[str] = Field(None, description="Faixa de referência (ex: Hb: 12–16 g/dL).")
    status: LabTestStatus = Field(default=LabTestStatus.pending, description="Status: pending, completed ou abnormal.")
    file_url: Optional[str] = Field(None, description="URL do arquivo de laudo (PDF ou imagem).")
    notes: Optional[str] = Field(None, description="Observações adicionais.")


class LabTestUpdate(CoreModel):
    result: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[LabTestStatus] = None
    file_url: Optional[str] = None
    notes: Optional[str] = None


class LabTestResponse(LabTestCreate, BaseEntitySchema):
    patient_id: UUID
    doctor_id: UUID


class LabTestListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[LabTestResponse]
