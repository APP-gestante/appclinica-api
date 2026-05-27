from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.crud import clinic as crud_clinic
from app.schemas.clinic import ClinicResponse, ClinicUpdate, ClinicWithAdminCreate

router = APIRouter()

@router.post("/clinics", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    clinic_in: ClinicWithAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["superadmin"]))
):
    """
    **Cadastrar uma nova clínica no sistema Lunna.**

    Esta rota permite que um superadmin crie uma nova clínica parceira (white-label) e, simultaneamente, configure o primeiro usuário administrador para essa clínica.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Exclusivo para usuários com o papel **`superadmin`**.

    ### 📥 Parâmetros de Entrada
    * **Dados da Clínica**: Nome, cores, endereço, telefone, email, fuso horário, etc.
    * **Dados do Admin Inicial**:
        * `admin_email`: Email único para o administrador da clínica.
        * `admin_name`: Nome completo do administrador.
        * `admin_password`: Senha inicial (deve ser alterada posteriormente).

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Retorna os detalhes da clínica recém-criada.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`403 FORBIDDEN`**: Usuário não possui privilégios de `superadmin`.
    """
    return await crud_clinic.create_clinic_with_admin(db, clinic_in=clinic_in)

@router.get("/clinics", response_model=List[ClinicResponse])
async def list_clinics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["superadmin"]))
):
    """
    **Listar todas as clínicas cadastradas.**

    Recupera uma lista de todas as clínicas gerenciadas pela plataforma Lunna.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Exclusivo para usuários com o papel **`superadmin`**.

    ### 📥 Parâmetros de Entrada
    * `skip` *(int, opcional)*: Número de registros a pular (paginação).
    * `limit` *(int, opcional)*: Número máximo de registros a retornar.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista de clínicas cadastradas.
    """
    return await crud_clinic.get_clinics(db, skip=skip, limit=limit)

@router.get("/clinics/{clinic_id}", response_model=ClinicResponse)
async def get_clinic(
    clinic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["superadmin"]))
):
    """
    **Obter detalhes de uma clínica específica.**

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Exclusivo para usuários com o papel **`superadmin`**.

    ### 📤 Retornos esperados
    * **`200 OK`**: Detalhes completos da clínica.
    * **`404 NOT FOUND`**: Clínica não encontrada.
    """
    clinic = await crud_clinic.get_clinic(db, clinic_id=clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

@router.put("/clinics/{clinic_id}", response_model=ClinicResponse)
async def update_clinic(
    clinic_id: UUID,
    clinic_in: ClinicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["superadmin"]))
):
    """
    **Atualizar dados de uma clínica.**

    Permite modificar informações como cores, logo, endereço e configurações regionais da clínica.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: Exclusivo para usuários com o papel **`superadmin`**.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados da clínica atualizados.
    * **`404 NOT FOUND`**: Clínica não encontrada.
    """
    db_clinic = await crud_clinic.get_clinic(db, clinic_id=clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return await crud_clinic.update_clinic(db, db_clinic=db_clinic, clinic_in=clinic_in)
