from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.crud import user as crud_user
from app.schemas.user import UserResponse, UserUpdate, ClinicResponse

router = APIRouter()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter dados do perfil do usuário.
    """
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar dados do perfil.
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = await crud_user.update_user(db, db_user=user, user_in=user_in)
    return user

@router.get("/{user_id}/clinic", response_model=ClinicResponse)
@cache(expire=300)  # Faz o cache dessa resposta no Redis por 5 minutos
async def get_user_clinic(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter informações da clínica do usuário.
    """
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    clinic = await crud_user.get_clinic_by_id(db, clinic_id=user.clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
        
    return clinic
