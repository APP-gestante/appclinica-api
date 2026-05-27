from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.models.enums import AppointmentStatus, PatientAppointmentStatus
from app.crud import appointment as crud_appointment
from app.schemas.appointment import (
    AppointmentResponse, AppointmentCreate, AppointmentCreateForPatient,
    AppointmentListResponse, AppointmentRescheduleRequest, AppointmentRescheduleApprove
)

router = APIRouter()

@router.get("/patients/{patient_id}/appointments", response_model=AppointmentListResponse)
async def list_patient_appointments(
    patient_id: UUID,
    status: str = Query(None, description="Filtrar por status da consulta (pending, confirmed, completed, cancelled)"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    offset: int = Query(0, ge=0, description="Ponto de partida para a paginação"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Listar todas as consultas agendadas para uma gestante específica.**

    Recupera o histórico completo e futuros agendamentos associados a uma paciente, permitindo filtros por status da consulta e suporte à paginação.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente (gestante).
    * `status` *(string, opcional, query)*: Status da consulta (`pending`, `confirmed`, `completed`, `cancelled`).
    * `limit` *(int, opcional, query)*: Quantidade de registros por página (padrão: 20, máximo: 100).
    * `offset` *(int, opcional, query)*: Deslocamento para paginação (padrão: 0).

    ### 📤 Retornos esperados
    * **`200 OK`**: Retorna a contagem total de registros condizentes com o filtro, o limite e deslocamento utilizados, e uma lista contendo os detalhes de cada agendamento.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
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
    """
    **Recuperar detalhes de uma consulta médica específica.**

    Retorna informações minuciosas de um agendamento individualizado pelo seu identificador único.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `appointment_id` *(UUID, na URL)*: Identificador único universal do agendamento solicitado.

    ### 📤 Retornos esperados
    * **`200 OK`**: Informações completas do agendamento (datas, horários, local, anotações clínicas, status de confirmação e dados da clínica).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Consulta com o `appointment_id` fornecido não foi encontrada.
    """
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.post("/patients/{patient_id}/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, tags=["appointments"])
async def create_appointment_for_patient(
    patient_id: UUID,
    obj_in: AppointmentCreateForPatient,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "secretary", "admin"])),
):
    """
    **Criar consulta diretamente vinculada a uma paciente.**

    Alternativa a `POST /doctors/{id}/appointments` — útil quando o fluxo parte da ficha da paciente.
    O `patient_id` vem da URL; o `doctor_id` vem no body.

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `secretary`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Consulta agendada com sucesso.
    """
    full_obj = AppointmentCreate(patient_id=patient_id, **obj_in.model_dump())
    return await crud_appointment.create_appointment(
        db, doctor_id=obj_in.doctor_id, clinic_id=current_user.clinic_id, obj_in=full_obj
    )


@router.post("/doctors/{doctor_id}/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    doctor_id: UUID,
    obj_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "secretary", "admin"]))
):
    """
    **Criar um novo agendamento de consulta para um médico.**

    Registra uma nova consulta no sistema associando uma paciente a um obstetra na clínica. Rota tipicamente utilizada pela secretária ou equipe clínica.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Permitida apenas para usuários com as roles **`doctor`**, **`secretary`** ou **`admin`**.

    ### 📥 Parâmetros de Entrada
    * `doctor_id` *(UUID, na URL)*: Identificador do médico com quem a consulta será agendada.
    * `patient_id` *(UUID, obrigatório, no corpo)*: Identificador da paciente gestante.
    * `date` *(date, obrigatório, no corpo)*: Data da consulta (`YYYY-MM-DD`).
    * `time` *(time, obrigatório, no corpo)*: Horário da consulta (`HH:MM`).
    * `duration_minutes` *(int, opcional, no corpo)*: Duração estimada (padrão: 30 minutos).
    * `type` *(string, opcional, no corpo)*: Tipo da consulta (`routine` (rotina), `ultrasound` (ultrassom), `lab` (exames)).
    * `location` *(string, opcional, no corpo)*: Consultório ou sala física da clínica.
    * `notes` *(string, opcional, no corpo)*: Notas ou observações preliminares.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Retorna os detalhes do agendamento recém-criado, incluindo o status inicial de confirmação.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`403 FORBIDDEN`**: Usuário logado não possui permissão funcional para agendar consultas (ex: paciente tentando agendar diretamente).
    """
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
    """
    **Confirmar a presença do paciente em uma consulta.**

    Usado pela gestante para validar sua ida à consulta agendada, alterando o status interno de confirmação e salvando a data/hora exata do aceite.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `appointment_id` *(UUID, na URL)*: Identificador único universal da consulta a ser confirmada.

    ### 📤 Retornos esperados
    * **`200 OK`**: Retorna os detalhes atualizados do agendamento com `patient_status` definido para `confirmed` e `confirmed_at` preenchido.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Consulta com o `appointment_id` fornecido não foi encontrada.
    """
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
    """
    **Solicitar a remarcação de uma consulta.**

    Registra um pedido formal de alteração de data/horário por parte da paciente gestante, contendo a justificativa e observações adicionais.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `appointment_id` *(UUID, na URL)*: Identificador do agendamento.
    * `reason` *(string, obrigatório, no corpo)*: Motivo da solicitação de alteração (ex: `conflito_pessoal`, `problema_saude`, `outro`).
    * `observation` *(string, opcional, no corpo)*: Observações detalhadas adicionais sobre a necessidade.

    ### 📤 Retornos esperados
    * **`200 OK`**: Agendamento atualizado com `patient_status` definido para `reschedule_requested`, registrando os motivos e a data da solicitação.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Consulta não encontrada.
    """
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
    """
    **Aprovar e efetivar a remarcação de uma consulta.**

    Processa a solicitação pendente de remarcação, estabelecendo a nova data e o novo horário definidos de comum acordo entre a clínica e a paciente.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Exclusivo para usuários com papéis funcionais **`doctor`**, **`secretary`** ou **`admin`**.

    ### 📥 Parâmetros de Entrada
    * `appointment_id` *(UUID, na URL)*: Identificador único universal da consulta.
    * `new_date` *(date, obrigatório, no corpo)*: Nova data acordada para a consulta (`YYYY-MM-DD`).
    * `new_time` *(time, obrigatório, no corpo)*: Novo horário acordado (`HH:MM`).

    ### 📤 Retornos esperados
    * **`200 OK`**: Detalhes da consulta atualizada com a nova data/horário e `patient_status` modificado para `reschedule_approved`.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`403 FORBIDDEN`**: Acesso negado para perfis não autorizados (ex: pacientes).
    * **`404 NOT FOUND`**: Consulta não encontrada.
    """
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
    reason: str = Query(..., description="Motivo do cancelamento definitivo da consulta"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Cancelar definitivamente uma consulta agendada.**

    Muda o status de um agendamento para cancelado e arquiva a justificativa. O cancelamento é definitivo e libera o slot na agenda médica correspondente.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `appointment_id` *(UUID, na URL)*: Identificador único universal da consulta a ser cancelada.
    * `reason` *(string, obrigatório, query)*: Descrição textual do motivo do cancelamento (ex: `paciente_desistiu`, `medica_cancelou`).

    ### 📤 Retornos esperados
    * **`204 NO CONTENT`**: Sucesso na solicitação de cancelamento. Não há conteúdo de retorno no corpo da resposta.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Consulta com o `appointment_id` fornecido não foi encontrada.
    """
    appointment = await crud_appointment.get_appointment(db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = {
        "status": AppointmentStatus.cancelled,
        "cancellation_reason": reason,
        "cancelled_at": datetime.utcnow()
    }
    await crud_appointment.update_appointment(db, db_obj=appointment, obj_in=update_data)
