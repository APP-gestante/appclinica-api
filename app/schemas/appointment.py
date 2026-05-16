from typing import Optional, List
from datetime import date, time, datetime
from uuid import UUID
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import AppointmentStatus, PatientAppointmentStatus, AppointmentType

class AppointmentBase(CoreModel):
    date: date
    time: time
    duration_minutes: int = 30
    type: AppointmentType = AppointmentType.routine
    location: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: UUID
    # The clinic_id will be derived from the doctor or patient in the service layer

class AppointmentUpdate(CoreModel):
    status: Optional[AppointmentStatus] = None
    patient_status: Optional[PatientAppointmentStatus] = None
    notes: Optional[str] = None

class AppointmentRescheduleRequest(CoreModel):
    reason: str
    observation: Optional[str] = None

class AppointmentRescheduleApprove(CoreModel):
    new_date: date
    new_time: time

class AppointmentResponse(AppointmentBase, BaseEntitySchema):
    patient_id: UUID
    doctor_id: UUID
    clinic_id: UUID
    datetime: datetime
    status: AppointmentStatus
    patient_status: PatientAppointmentStatus
    confirmed_at: Optional[datetime] = None
    reschedule_reason: Optional[str] = None
    reschedule_observation: Optional[str] = None
    new_date: Optional[date] = None
    new_time: Optional[time] = None

class AppointmentListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[AppointmentResponse]
