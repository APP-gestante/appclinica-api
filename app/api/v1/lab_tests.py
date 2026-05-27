from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.models.enums import LabTestType
from app.crud import lab_tests as crud_lab
from app.schemas.lab_tests import LabTestCreate, LabTestResponse, LabTestListResponse

router = APIRouter()


@router.get("/{patient_id}/lab-tests", response_model=LabTestListResponse, tags=["exams"])
async def list_lab_tests(
    patient_id: UUID,
    type: Optional[LabTestType] = Query(None, description="Filtrar por tipo de exame"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar exames laboratoriais da paciente.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de exames.
    """
    total, items = await crud_lab.get_lab_tests(
        db, patient_id=patient_id, type=type, skip=offset, limit=limit
    )
    return {"total": total, "limit": limit, "offset": offset, "data": items}


@router.post(
    "/{patient_id}/lab-tests",
    response_model=LabTestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["exams"],
)
async def create_lab_test(
    patient_id: UUID,
    obj_in: LabTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """
    **Registrar resultado de exame laboratorial.**

    ### 📌 Requisitos de Segurança
    * RBAC: `doctor`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Exame registrado com sucesso.
    """
    return await crud_lab.create_lab_test(
        db, patient_id=patient_id, doctor_id=current_user.id, obj_in=obj_in
    )


@router.get("/lab-tests/{lab_test_id}", response_model=LabTestResponse, tags=["exams"])
async def get_lab_test(
    lab_test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter detalhe de um exame laboratorial.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados completos do exame.
    * **`404 NOT FOUND`**: Exame não encontrado.
    """
    lab_test = await crud_lab.get_lab_test(db, lab_test_id=lab_test_id)
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test
