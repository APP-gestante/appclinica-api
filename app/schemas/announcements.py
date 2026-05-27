from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import AnnouncementCategory


class AnnouncementCreate(CoreModel):
    category: AnnouncementCategory = Field(
        ..., description="Categoria do aviso (agenda, saude, clinica, geral).", examples=["agenda"]
    )
    title: str = Field(..., description="Título do aviso.", examples=["Recesso de Carnaval"])
    short_description: str = Field(
        ..., description="Descrição curta exibida na listagem (máx 500 chars).",
        examples=["A clínica não atenderá nos dias 12 e 13 de fevereiro."],
    )
    full_description: str = Field(
        ..., description="Texto completo exibido ao expandir o aviso.",
        examples=["A clínica estará fechada nos dias 12 e 13 de fevereiro devido ao feriado de Carnaval. Retornaremos normalmente na quarta-feira, dia 14."],
    )
    expires_at: Optional[datetime] = Field(
        None, description="Data/hora de expiração do aviso (UTC). Nulo = sem expiração.",
        examples=["2024-02-14T00:00:00Z"],
    )


class AnnouncementResponse(AnnouncementCreate, BaseEntitySchema):
    clinic_id: UUID = Field(..., description="ID da clínica dona do aviso.")
    is_new: bool = Field(..., description="True se o aviso foi criado há menos de 7 dias.")


class AnnouncementListResponse(CoreModel):
    total: int = Field(..., description="Total de avisos encontrados.")
    limit: int = Field(..., description="Limite por página.")
    offset: int = Field(..., description="Offset de paginação.")
    data: List[AnnouncementResponse]
