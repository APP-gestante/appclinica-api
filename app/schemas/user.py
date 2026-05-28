from typing import Optional
from datetime import date
import datetime as dt
from uuid import UUID
from pydantic import EmailStr, Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import UserRole

# -- User --

# -- User --

class UserBase(CoreModel):
    email: EmailStr = Field(..., description="Endereço de email único do usuário.", examples=["maria@clinic.com"])
    name: str = Field(..., description="Nome completo do usuário.", examples=["Maria da Silva"])
    role: UserRole = Field(default=UserRole.patient, description="Papel funcional ou nível de permissão (patient, doctor, secretary, admin).", examples=["patient"])
    phone: Optional[str] = Field(None, description="Número de telefone para contato.", examples=["(11) 99999-9999"])
    avatar_url: Optional[str] = Field(None, description="URL da foto de perfil do usuário.", examples=["https://clinic.com/avatars/maria.jpg"])
    date_of_birth: Optional[dt.date] = Field(None, description="Data de nascimento do usuário.", examples=["1990-05-15"])

class UserCreate(UserBase):
    password: str = Field(..., description="Senha forte para login na plataforma.", examples=["senha_secreta_123"])
    clinic_id: UUID = Field(..., description="Identificador único (UUID) da clínica associada.", examples=["123e4567-e89b-12d3-a456-426614174000"])

class UserUpdate(CoreModel):
    name: Optional[str] = Field(None, description="Nome completo atualizado do usuário.", examples=["Maria da Silva Santos"])
    phone: Optional[str] = Field(None, description="Número de telefone atualizado.", examples=["(11) 98888-8888"])
    avatar_url: Optional[str] = Field(None, description="URL atualizada do avatar.", examples=["https://clinic.com/avatars/maria_new.jpg"])

class UserResponse(UserBase, BaseEntitySchema):
    clinic_id: Optional[UUID] = Field(None, description="Identificador único (UUID) da clínica associada.")
    is_active: bool = Field(..., description="Indica se a conta de usuário está ativa e habilitada para login.", examples=[True])

# -- Patient --

class PatientCreate(CoreModel):
    doctor_id: UUID = Field(..., description="Identificador único (UUID) do médico/obstetra responsável.")
    prontuario: str = Field(..., description="Número de registro ou identificador do prontuário médico na clínica.", examples=["PR-98765"])
    lmp_date: dt.date = Field(..., description="Data da Última Menstruação (DUM), usada no cálculo de semanas gestacionais.", examples=["2023-11-01"])
    edd: dt.date = Field(..., description="Data Provável do Parto (DPP) estimada matematicamente.", examples=["2024-08-07"])
    height_cm: Optional[str] = Field(None, description="Altura da gestante em centímetros.", examples=["165"])
    weight_initial_kg: Optional[str] = Field(None, description="Peso inicial da gestante no início do pré-natal em kg.", examples=["62.5"])
    imc: Optional[str] = Field(None, description="Índice de Massa Corporal (IMC) inicial calculado.", examples=["22.9"])
    blood_type: Optional[str] = Field(None, description="Grupo sanguíneo e fator Rh da gestante.", examples=["O+"])
    acompanhante: Optional[str] = Field(None, description="Nome do acompanhante principal indicado pela gestante.", examples=["João da Silva"])
    hospital: Optional[str] = Field(None, description="Maternidade ou hospital escolhido para o parto.", examples=["Hospital Maternidade Santa Joana"])

class PatientResponse(PatientCreate, BaseEntitySchema):
    user_id: UUID = Field(..., description="Identificador único do usuário associado a este perfil de paciente.")
    current_week: Optional[int] = Field(None, description="Idade gestacional calculada dinamicamente em semanas.", examples=[24])

class PatientUpdate(CoreModel):
    height_cm: Optional[str] = Field(None, description="Altura em centímetros.", examples=["165"])
    weight_initial_kg: Optional[str] = Field(None, description="Peso inicial em kg.", examples=["62.5"])
    imc: Optional[str] = Field(None, description="Índice de Massa Corporal.", examples=["22.9"])
    blood_type: Optional[str] = Field(None, description="Grupo sanguíneo e fator Rh.", examples=["O+"])
    acompanhante: Optional[str] = Field(None, description="Nome do acompanhante.", examples=["João da Silva"])
    hospital: Optional[str] = Field(None, description="Maternidade escolhida.", examples=["Hospital Maternidade Santa Joana"])
    risk_level: Optional[str] = Field(None, description="Nível de risco (low, medium, high).", examples=["low"])
    number_of_fetuses: Optional[int] = Field(None, description="Número de fetos.", examples=[1])
    parity: Optional[str] = Field(None, description="Paridade (ex: G1P0).", examples=["G1P0"])
    cesarean_predicted: Optional[bool] = Field(None, description="Previsão de cesárea.", examples=[False])

class PatientDetailResponse(PatientResponse):
    user: UserResponse = Field(..., description="Dados do usuário associado.")

class PatientListItemResponse(CoreModel):
    id: UUID = Field(..., description="ID do perfil de paciente.")
    user_id: UUID
    prontuario: str
    current_week: Optional[int] = None
    edd: date
    risk_level: str
    user: UserResponse

class PatientListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: list[PatientListItemResponse]

class ProntuarioResponse(CoreModel):
    patient_id: UUID
    dados_clinicos: PatientResponse
    user: UserResponse
    updated_at: Optional[date] = None

# -- Clinic schemas moved to clinic.py --

