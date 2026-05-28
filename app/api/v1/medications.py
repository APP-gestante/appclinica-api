from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.crud import medications as crud_med
from app.schemas.medications import MedicationCreate, MedicationUpdate, MedicationResponse, MedicationListResponse

router = APIRouter()


@router.get("/{patient_id}/medications", response_model=MedicationListResponse, tags=["medications"])
async def list_medications(
    patient_id: UUID,
    active: Optional[bool] = Query(None, description="Filtrar apenas ativos (true) ou inativos (false)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar prescrições de medicamentos da paciente.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de medicamentos.
    """
    total, items = await crud_med.get_medications(
        db, patient_id=patient_id, active=active, skip=offset, limit=limit
    )
    return {"total": total, "limit": limit, "offset": offset, "data": items}


@router.post(
    "/{patient_id}/medications",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["medications"],
)
async def create_medication(
    patient_id: UUID,
    obj_in: MedicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Prescrever medicamento para a paciente.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Prescrição registrada com sucesso.
    """
    return await crud_med.create_medication(
        db, patient_id=patient_id, doctor_id=current_user.id, obj_in=obj_in
    )


@router.patch("/medications/{medication_id}", response_model=MedicationResponse, tags=["medications"])
async def update_medication(
    medication_id: UUID,
    obj_in: MedicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Atualizar ou descontinuar medicamento.**

    Permite ajustar dosagem, frequência, instruções ou marcar como inativo (`active: false`).

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`200 OK`**: Medicamento atualizado.
    * **`404 NOT FOUND`**: Medicamento não encontrado.
    """
    medication = await crud_med.get_medication(db, medication_id=medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    return await crud_med.update_medication(db, medication=medication, obj_in=obj_in)
