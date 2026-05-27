from typing import Optional
from pydantic import EmailStr, Field
from app.schemas.base import CoreModel, BaseEntitySchema

class ClinicBase(CoreModel):
    name: str = Field(..., description="Nome da clínica de obstetrícia / parceira white-label.", examples=["Clínica Lunna"])
    logo_url: Optional[str] = Field(None, description="URL do logotipo personalizado da clínica.", examples=["https://lunnaclinica.com/logo.png"])
    primary_color: Optional[str] = Field(None, description="Código hexadecimal da cor primária da marca no aplicativo móvel.", examples=["#8DAA91"])
    secondary_color: Optional[str] = Field(None, description="Código hexadecimal da cor secundária da marca no aplicativo móvel.", examples=["#E5987D"])
    accent_color: Optional[str] = Field(None, description="Código hexadecimal da cor de destaque da marca.", examples=["#4A5E51"])
    address: Optional[str] = Field(None, description="Endereço físico completo da clínica.", examples=["Av. Paulista, 1000 - Bela Vista, São Paulo - SP"])
    phone: Optional[str] = Field(None, description="Telefone de contato da clínica.", examples=["(11) 3000-0000"])
    email: Optional[EmailStr] = Field(None, description="Endereço de email institucional da clínica.", examples=["contato@lunnaclinica.com"])
    website: Optional[str] = Field(None, description="Endereço eletrônico (site oficial) da clínica.", examples=["https://lunnaclinica.com"])
    timezone: str = Field("America/Sao_Paulo", description="Fuso horário da clínica.", examples=["America/Sao_Paulo"])
    language: str = Field("pt-BR", description="Idioma padrão da clínica.", examples=["pt-BR"])

class ClinicCreate(ClinicBase):
    pass

class ClinicUpdate(CoreModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

class ClinicResponse(ClinicBase, BaseEntitySchema):
    pass

class ClinicWithAdminCreate(ClinicCreate):
    admin_email: EmailStr = Field(..., description="Email do administrador inicial da clínica.", examples=["admin@novaclinica.com"])
    admin_name: str = Field(..., description="Nome do administrador inicial da clínica.", examples=["Admin Nova Clínica"])
    admin_password: str = Field(..., description="Senha do administrador inicial da clínica.", examples=["senha_segura123"])
