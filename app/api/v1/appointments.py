from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.models.enums import AppointmentStatus, PatientAppointmentStatus
from app.crud import appointment as crud_appointment
from app.schemas.appointment import (
    AppointmentResponse, AppointmentCreate, AppointmentListResponse, 
    AppointmentRescheduleRequest, AppointmentRescheduleApprove
)

router = APIRouter()

@router.get("/patients/{patient_id}/appointments", response_model=AppointmentListResponse)
async def list_patient_appointments(
    patient_id: UUID,
    status: str = Query(None, description="pending, confirmed, completed, cancelled"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = await crud_appointment.get_patient_appointments(
        db, patient_id=patient_id, skip=offset, limit=limit, status=status
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": items
    }

@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.post("/doctors/{doctor_id}/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    doctor_id: UUID,
    obj_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "secretary", "admin"]))
):
    # O clinic_id será herdado do usuário criador, na vida real isso seria mais complexo
    clinic_id = current_user.clinic_id
    appointment = await crud_appointment.create_appointment(
        db, doctor_id=doctor_id, clinic_id=clinic_id, obj_in=obj_in
    )
    return appointment

@router.patch("/appointments/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = {
        "patient_status": PatientAppointmentStatus.confirmed,
        "confirmed_at": datetime.utcnow()
    }
    return await crud_appointment.update_appointment(db, db_obj=appointment, obj_in=update_data)

@router.post("/appointments/{appointment_id}/reschedule-request", response_model=AppointmentResponse)
async def request_reschedule(
    appointment_id: UUID,
    request: AppointmentRescheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = {
        "patient_status": PatientAppointmentStatus.reschedule_requested,
        "reschedule_reason": request.reason,
        "reschedule_observation": request.observation,
        "reschedule_requested_at": datetime.utcnow(),
        "reschedule_requested_by": current_user.id
    }
    return await crud_appointment.update_appointment(db, db_obj=appointment, obj_in=update_data)

@router.patch("/appointments/{appointment_id}/reschedule/approve", response_model=AppointmentResponse)
async def approve_reschedule(
    appointment_id: UUID,
    request: AppointmentRescheduleApprove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "secretary", "admin"]))
):
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = {
        "patient_status": PatientAppointmentStatus.reschedule_approved,
        "date": request.new_date,
        "time": request.new_time,
        "datetime": datetime.combine(request.new_date, request.new_time),
        "reschedule_approved_at": datetime.utcnow(),
        "reschedule_approved_by": current_user.id
    }
    return await crud_appointment.update_appointment(db, db_obj=appointment, obj_in=update_data)

@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: UUID,
    reason: str = Query(..., description="Motivo do cancelamento"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = {
        "status": AppointmentStatus.cancelled,
        "cancellation_reason": reason,
        "cancelled_at": datetime.utcnow()
    }
    await crud_appointment.update_appointment(db, db_obj=appointment, obj_in=update_data)
