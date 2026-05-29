from uuid import UUID
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.core.security import get_password_hash
from app.models.user import User
from app.crud import patient as crud_patient
from app.crud import patient_anamnesis as crud_anamnesis
from app.schemas.patient_anamnesis import AnamnesisCreate, AnamnesisResponse
from app.schemas.user import (
    PatientDetailResponse,
    PatientListResponse,
    PatientListItemResponse,
    PatientResponse,
    PatientUpdate,
    ProntuarioResponse,
    UserResponse,
    UserCreate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Grupo 2 — Dados da paciente
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}", response_model=PatientDetailResponse, tags=["patients"])
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter dados gestacionais completos da paciente.**

    Retorna todos os campos do perfil `Patient` (semana gestacional, DUM, DPP, risco, etc.)
    junto com os dados básicos do `User` associado (nome, email, telefone).

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados gestacionais + dados do usuário.
    * **`404 NOT FOUND`**: Paciente não encontrada.
    """
    row = await crud_patient.get_patient_with_user(db, patient_id=patient_id)
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient, user = row
    return {**PatientResponse.model_validate(patient).model_dump(), "user": user}


# ---------------------------------------------------------------------------
# Grupo 6 — Prontuário
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/prontuario", response_model=ProntuarioResponse, tags=["patients"])
async def get_prontuario(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter prontuário gestacional completo.**

    Retorna dados clínicos da paciente (Patient) e dados cadastrais do usuário (User) agregados.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Prontuário completo agregado.
    * **`404 NOT FOUND`**: Paciente não encontrada.
    """
    row = await crud_patient.get_patient_with_user(db, patient_id=patient_id)
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient, user = row
    return {
        "patient_id": patient.id,
        "dados_clinicos": patient,
        "user": user,
        "updated_at": patient.updated_at,
    }


@router.put("/patients/{patient_id}/prontuario", response_model=PatientResponse, tags=["patients"])
async def update_prontuario(
    patient_id: UUID,
    obj_in: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Atualizar campos editáveis do prontuário gestacional.**

    Somente campos presentes no body são atualizados (partial update).

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados atualizados retornados.
    * **`404 NOT FOUND`**: Paciente não encontrada.
    """
    patient = await crud_patient.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return await crud_patient.update_patient(db, patient=patient, obj_in=obj_in)


# ---------------------------------------------------------------------------
# Grupo 8a — Dashboard e pacientes do médico
# ---------------------------------------------------------------------------

@router.get("/doctors/{doctor_id}/patients", response_model=PatientListResponse, tags=["doctor"])
async def list_doctor_patients(
    doctor_id: UUID,
    search: Optional[str] = Query(None, description="Busca por nome ou prontuário"),
    risk_level: Optional[str] = Query(None, description="Filtro de risco: low, medium, high"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Listar pacientes do médico com filtros de busca e risco.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de pacientes com semana gestacional e nível de risco.
    """
    total, rows = await crud_patient.get_doctor_patients(
        db, doctor_id=doctor_id, search=search, risk_level=risk_level, skip=offset, limit=limit
    )
    items = [
        PatientListItemResponse(
            id=p.id,
            user_id=p.user_id,
            prontuario=p.prontuario,
            current_week=p.current_week,
            edd=p.edd,
            risk_level=p.risk_level,
            user=u,
        )
        for p, u in rows
    ]
    return {"total": total, "limit": limit, "offset": offset, "data": items}


@router.get("/doctors/{doctor_id}/dashboard", tags=["doctor"])
async def get_doctor_dashboard(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Estatísticas do dashboard do médico.**

    Retorna consultas do dia e total de pacientes ativas.

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.
    """
    return await crud_patient.get_doctor_dashboard(db, doctor_id=doctor_id)


@router.get("/doctors/{doctor_id}/agenda", tags=["doctor"])
async def get_doctor_agenda(
    doctor_id: UUID,
    view: str = Query("day", description="Visualização: day | week | births"),
    reference_date: Optional[date] = Query(None, alias="date", description="Data de referência (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Agenda do médico em três visualizações.**

    * `day` — consultas do dia, ordenadas por horário.
    * `week` — consultas da semana a partir da data de referência.
    * `births` — partos previstos nos próximos 60 dias.

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.
    """
    ref = reference_date or date.today()

    if view == "day":
        appointments = await crud_patient.get_doctor_agenda_day(db, doctor_id=doctor_id, day=ref)
        return {
            "view": "day",
            "date": str(ref),
            "appointments": [
                {
                    "id": str(a.id),
                    "date": str(a.date),
                    "time": str(a.time),
                    "duration_minutes": a.duration_minutes,
                    "type": a.type,
                    "status": a.status,
                    "patient_status": a.patient_status,
                    "location": a.location,
                    "notes": a.notes,
                    "patient_id": str(a.patient_id),
                    "patient": {
                        "id": str(a.patient.user.id) if a.patient and a.patient.user else None,
                        "name": a.patient.user.name if a.patient and a.patient.user else None,
                    } if a.patient else None,
                }
                for a in appointments
            ],
        }

    if view == "week":
        appointments = await crud_patient.get_doctor_agenda_week(db, doctor_id=doctor_id, start=ref)
        return {
            "view": "week",
            "start": str(ref),
            "appointments": [
                {
                    "id": str(a.id),
                    "date": str(a.date),
                    "time": str(a.time),
                    "duration_minutes": a.duration_minutes,
                    "type": a.type,
                    "status": a.status,
                    "patient_status": a.patient_status,
                    "location": a.location,
                    "notes": a.notes,
                    "patient_id": str(a.patient_id),
                    "patient": {
                        "id": str(a.patient.user.id) if a.patient and a.patient.user else None,
                        "name": a.patient.user.name if a.patient and a.patient.user else None,
                    } if a.patient else None,
                }
                for a in appointments
            ],
        }

    if view == "births":
        rows = await crud_patient.get_doctor_upcoming_births(db, doctor_id=doctor_id)
        return {
            "view": "births",
            "upcoming_births": [
                {
                    "patient_id": str(p.id),
                    "name": u.name,
                    "edd": str(p.edd),
                    "current_week": p.current_week,
                    "risk_level": p.risk_level,
                    "hospital": p.hospital,
                }
                for p, u in rows
            ],
        }

    raise HTTPException(status_code=400, detail="view must be 'day', 'week', or 'births'")


# ---------------------------------------------------------------------------
# Grupo 8b — Dashboard e cadastro de paciente (secretária)
# ---------------------------------------------------------------------------

@router.get("/secretary/dashboard", tags=["secretary"])
async def get_secretary_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["secretary", "admin"])),
):
    """
    **Estatísticas do dashboard da secretária.**

    Retorna totais do dia para toda a clínica: consultas, confirmadas, pendentes e total de pacientes.

    ### 📌 Requisitos de Segurança
    * RBAC: `secretary`, `admin`.
    """
    return await crud_patient.get_secretary_dashboard(db, clinic_id=current_user.clinic_id)


@router.get("/clinics/{clinic_id}/reports/daily", tags=["secretary"])
async def get_daily_report(
    clinic_id: UUID,
    report_date: Optional[date] = Query(None, alias="date", description="Data do relatório (YYYY-MM-DD, padrão: hoje)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["secretary", "admin"])),
):
    """
    **Relatório diário de atividades da clínica.**

    Retorna totais de consultas, confirmadas, canceladas e novas pacientes no dia.

    ### 📌 Requisitos de Segurança
    * RBAC: `secretary`, `admin`.
    """
    day = report_date or date.today()
    return await crud_patient.get_daily_report(db, clinic_id=clinic_id, day=day)


@router.post("/patients", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["secretary"])
async def create_patient(
    obj_in: UserCreate,
    doctor_id: UUID = Query(..., description="UUID do médico responsável"),
    prontuario: str = Query(..., description="Número do prontuário"),
    lmp_date: date = Query(..., description="Data da última menstruação (YYYY-MM-DD)"),
    edd: date = Query(..., description="Data provável do parto (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["secretary", "admin"])),
):
    """
    **Cadastrar nova paciente na clínica.**

    Cria o `User` (role=patient) e o `Patient` em uma única transação.

    ### 📌 Requisitos de Segurança
    * RBAC: `secretary`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Usuário criado com sucesso.
    """
    password_hash = get_password_hash(obj_in.password)
    user, _patient = await crud_patient.create_patient_with_user(
        db,
        name=obj_in.name,
        email=obj_in.email,
        phone=obj_in.phone,
        password_hash=password_hash,
        clinic_id=obj_in.clinic_id,
        doctor_id=doctor_id,
        prontuario=prontuario,
        lmp_date=lmp_date,
        edd=edd,
    )
    return user


# ── Anamnese ──────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/anamnesis", response_model=AnamnesisResponse, tags=["patients"])
async def get_anamnesis(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna a anamnese estruturada da gestante."""
    ana = await crud_anamnesis.get_anamnesis(db, patient_id=patient_id)
    if not ana:
        raise HTTPException(status_code=404, detail="Anamnesis not found")
    return ana


@router.post("/patients/{patient_id}/anamnesis", response_model=AnamnesisResponse, tags=["patients"])
async def upsert_anamnesis(
    patient_id: UUID,
    obj_in: AnamnesisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Cria ou atualiza a anamnese da gestante (upsert)."""
    patient = await crud_patient.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return await crud_anamnesis.upsert_anamnesis(db, patient_id=patient_id, obj_in=obj_in)
