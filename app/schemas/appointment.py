from typing import Optional, List
import datetime as dt
from uuid import UUID
from pydantic import Field
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import AppointmentStatus, PatientAppointmentStatus, AppointmentType

class AppointmentBase(CoreModel):
    date: dt.date = Field(..., description="Data agendada da consulta médica.", examples=["2024-02-15"])
    time: dt.time = Field(..., description="Horário de início da consulta.", examples=["14:30"])
    duration_minutes: int = Field(default=30, description="Duração estimada do atendimento clínico em minutos.", examples=[30])
    type: AppointmentType = Field(default=AppointmentType.routine, description="Tipo/natureza do atendimento (routine, ultrasound, lab).", examples=["routine"])
    location: Optional[str] = Field(None, description="Local ou consultório físico onde ocorrerá o atendimento.", examples=["Sala 302 - Clínica Lunna"])
    notes: Optional[str] = Field(None, description="Anotações e instruções especiais para o paciente.", examples=["Acompanhamento de rotina de pré-natal."])

class AppointmentCreate(AppointmentBase):
    patient_id: UUID = Field(..., description="Identificador único (UUID) da gestante/paciente.")

class AppointmentCreateForPatient(AppointmentBase):
    """Schema para criar consulta com patient_id vindo da URL (fluxo centrado na paciente)."""
    doctor_id: UUID = Field(..., description="Identificador único (UUID) do médico responsável.")

class AppointmentUpdate(CoreModel):
    status: Optional[AppointmentStatus] = Field(None, description="Status de andamento da consulta (pending, confirmed, completed, cancelled).")
    patient_status: Optional[PatientAppointmentStatus] = Field(None, description="Status de confirmação ou remarcação por parte do paciente (pending, confirmed, reschedule_requested, reschedule_approved).")
    notes: Optional[str] = Field(None, description="Notas clínicas adicionais ou comentários.")

class AppointmentRescheduleRequest(CoreModel):
    reason: str = Field(..., description="Motivo pelo qual a paciente está solicitando remarcar a consulta.", examples=["conflito_pessoal"])
    observation: Optional[str] = Field(None, description="Informações ou observações adicionais sobre o pedido de remarcação.", examples=["Não estarei na cidade nesse dia."])

class AppointmentRescheduleApprove(CoreModel):
    new_date: dt.date = Field(..., description="Nova data acordada para a realização da consulta.", examples=["2024-02-22"])
    new_time: dt.time = Field(..., description="Novo horário acordado para a consulta.", examples=["15:00"])

class AppointmentResponse(AppointmentBase, BaseEntitySchema):
    patient_id: UUID = Field(..., description="Identificador único da paciente gestante.")
    doctor_id: UUID = Field(..., description="Identificador único do médico obstetra.")
    clinic_id: UUID = Field(..., description="Identificador único da clínica associada.")
    datetime: dt.datetime = Field(..., description="Data e hora combinadas em formato completo ISO 8601.", examples=["2024-02-15T14:30:00Z"])
    status: AppointmentStatus = Field(..., description="Status geral do agendamento.")
    patient_status: PatientAppointmentStatus = Field(..., description="Status de resposta da paciente em relação à consulta.")
    confirmed_at: Optional[dt.datetime] = Field(None, description="Carimbo de data/hora de quando a paciente confirmou a consulta.")
    reschedule_reason: Optional[str] = Field(None, description="Justificativa arquivada para a solicitação de remarcação.")
    reschedule_observation: Optional[str] = Field(None, description="Anotações textuais da solicitação de remarcação.")
    new_date: Optional[dt.date] = Field(None, description="Nova data em caso de solicitação de remarcação.")
    new_time: Optional[dt.time] = Field(None, description="Novo horário em caso de solicitação de remarcação.")

class AppointmentListResponse(CoreModel):
    total: int = Field(..., description="Contagem total de registros localizados que atendem aos filtros.", examples=[12])
    limit: int = Field(..., description="Quantidade máxima de registros retornados na página atual.", examples=[20])
    offset: int = Field(..., description="Deslocamento (número de registros ignorados) usado para paginação.", examples=[0])
    data: List[AppointmentResponse] = Field(..., description="Lista contendo os registros de agendamentos encontrados.")
