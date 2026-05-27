from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.crud import exams as crud_exams
from app.schemas.exams import (
    UltrasoundCreate,
    UltrasoundResponse,
    UltrasoundListResponse,
    VaccineCreate,
    VaccineUpdate,
    VaccineResponse,
    VaccineListResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Ultrassom
# ---------------------------------------------------------------------------

@router.post(
    "/{patient_id}/ultrasounds",
    response_model=UltrasoundResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ultrasound(
    patient_id: UUID,
    obj_in: UltrasoundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Registrar laudo de ultrassonografia (USG) obstétrica.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Laudo persistido com sucesso.
    * **`401 UNAUTHORIZED`**: Token inválido ou expirado.
    """
    return await crud_exams.create_ultrasound(
        db, patient_id=patient_id, doctor_id=current_user.id, obj_in=obj_in
    )


@router.get("/{patient_id}/ultrasounds", response_model=UltrasoundListResponse)
async def list_ultrasounds(
    patient_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="Registros por página"),
    offset: int = Query(0, ge=0, description="Offset de paginação"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar histórico de ultrassonografias da paciente.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de ultrassons reais do banco de dados.
    """
    total, items = await crud_exams.get_ultrasounds(
        db, patient_id=patient_id, skip=offset, limit=limit
    )
    return {"total": total, "limit": limit, "offset": offset, "data": items}


# ---------------------------------------------------------------------------
# Vacinas
# ---------------------------------------------------------------------------

@router.post(
    "/{patient_id}/vaccines",
    response_model=VaccineResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vaccine(
    patient_id: UUID,
    obj_in: VaccineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Registrar vacina ou agendamento de vacinação.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Vacina registrada com sucesso.
    """
    return await crud_exams.create_vaccine(
        db, patient_id=patient_id, doctor_id=current_user.id, obj_in=obj_in
    )


@router.get("/{patient_id}/vaccines", response_model=VaccineListResponse)
async def list_vaccines(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar cartão de vacinação da paciente.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de vacinas.
    """
    total, items = await crud_exams.get_vaccines(
        db, patient_id=patient_id, skip=offset, limit=limit
    )
    return {"total": total, "limit": limit, "offset": offset, "data": items}


@router.patch("/vaccines/{vaccine_id}", response_model=VaccineResponse)
async def update_vaccine(
    vaccine_id: UUID,
    obj_in: VaccineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Atualizar status ou reações de uma vacina.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`200 OK`**: Vacina atualizada.
    * **`404 NOT FOUND`**: Vacina não encontrada.
    """
    vaccine = await crud_exams.get_vaccine(db, vaccine_id=vaccine_id)
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    return await crud_exams.update_vaccine(db, vaccine=vaccine, obj_in=obj_in)
