from uuid import UUID
from typing import Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import User, Patient
from app.models.enums import BabyNameGender
from app.crud import baby_names as crud_baby_names
from app.schemas.baby_names import BabyNameListResponse, BabyNameResponse, FavoriteResponse

router = APIRouter()


async def _patient_favorite_ids(db: AsyncSession, user: User) -> Set[UUID]:
    """Return set of baby_name_ids favorited by the patient linked to this user. Empty if not a patient."""
    if user.role != "patient":
        return set()
    result = await db.execute(select(Patient).where(Patient.user_id == user.id))
    patient = result.scalar_one_or_none()
    if not patient:
        return set()
    return await crud_baby_names.get_favorite_ids(db, patient_id=patient.id)


@router.get("/baby-names", response_model=BabyNameListResponse)
async def list_baby_names(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gender: Optional[BabyNameGender] = None,
    search: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar nomes de bebê com filtros opcionais.**

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de nomes com popularidade, origem e significado.
      O campo `is_favorite` é preenchido automaticamente para pacientes autenticados.
    """
    total, names = await crud_baby_names.get_baby_names(
        db, limit=limit, offset=offset, gender=gender, search=search
    )
    fav_ids = await _patient_favorite_ids(db, current_user)

    data = []
    for n in names:
        item = BabyNameResponse.model_validate(n)
        item.is_favorite = n.id in fav_ids
        data.append(item)

    return {"total": total, "limit": limit, "offset": offset, "data": data}


@router.post(
    "/patients/{patient_id}/baby-names/{name_id}/favorite",
    response_model=FavoriteResponse,
    status_code=201,
)
async def add_favorite(
    patient_id: UUID,
    name_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Adicionar nome de bebê aos favoritos da paciente.**

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Nome adicionado aos favoritos.
    * **`409 CONFLICT`**: Nome já está nos favoritos.
    """
    existing = await crud_baby_names.get_favorite(db, patient_id=patient_id, baby_name_id=name_id)
    if existing:
        raise HTTPException(status_code=409, detail="Already in favorites")
    fav = await crud_baby_names.add_favorite(db, patient_id=patient_id, baby_name_id=name_id)
    return {"patient_id": fav.patient_id, "baby_name_id": fav.baby_name_id}


@router.delete(
    "/patients/{patient_id}/baby-names/{name_id}/favorite",
    status_code=204,
)
async def remove_favorite(
    patient_id: UUID,
    name_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Remover nome de bebê dos favoritos da paciente.**

    ### 📤 Retornos esperados
    * **`204 NO CONTENT`**: Favorito removido.
    * **`404 NOT FOUND`**: Favorito não encontrado.
    """
    fav = await crud_baby_names.get_favorite(db, patient_id=patient_id, baby_name_id=name_id)
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await crud_baby_names.remove_favorite(db, fav=fav)


@router.get(
    "/patients/{patient_id}/baby-names/favorites",
    response_model=BabyNameListResponse,
)
async def list_favorites(
    patient_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar nomes de bebê favoritos da paciente.**

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de nomes favoritos.
    """
    total, names = await crud_baby_names.get_favorites(
        db, patient_id=patient_id, limit=limit, offset=offset
    )
    data = []
    for n in names:
        item = BabyNameResponse.model_validate(n)
        item.is_favorite = True
        data.append(item)
    return {"total": total, "limit": limit, "offset": offset, "data": data}
