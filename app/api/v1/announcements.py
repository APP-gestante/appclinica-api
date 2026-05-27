from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.models.enums import AnnouncementCategory
from app.crud import announcements as crud_ann
from app.schemas.announcements import AnnouncementCreate, AnnouncementResponse, AnnouncementListResponse

router = APIRouter()


@router.get("/clinics/{clinic_id}/announcements", response_model=AnnouncementListResponse)
async def list_announcements(
    clinic_id: UUID,
    category: Optional[AnnouncementCategory] = Query(None, description="Filtrar por categoria"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar avisos da clínica.**

    Retorna avisos não expirados, filtrados opcionalmente por categoria. O campo `is_new` indica
    avisos criados nos últimos 7 dias.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de avisos com campo `is_new`.
    """
    total, items = await crud_ann.get_announcements(
        db, clinic_id=clinic_id, category=category, skip=offset, limit=limit
    )
    return {"total": total, "limit": limit, "offset": offset, "data": items}


@router.post(
    "/clinics/{clinic_id}/announcements",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_announcement(
    clinic_id: UUID,
    obj_in: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["secretary", "admin"])),
):
    """
    **Publicar novo aviso na clínica.**

    ### 📌 Requisitos de Segurança
    * RBAC: `secretary`, `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Aviso publicado com sucesso.
    """
    return await crud_ann.create_announcement(db, clinic_id=clinic_id, obj_in=obj_in)
