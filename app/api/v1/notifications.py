from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.crud import notifications as crud_notifications
from app.schemas.notifications import NotificationResponse, NotificationListResponse

router = APIRouter()


@router.get("/users/{user_id}/notifications", response_model=NotificationListResponse)
async def list_notifications(
    user_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Listar notificações do usuário.**

    ### 📌 Requisitos de Segurança
    * Requer `Authorization: Bearer <token>` válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de notificações.
    * **`401 UNAUTHORIZED`**: Token inválido ou expirado.
    """
    total, notifications = await crud_notifications.get_notifications(
        db, user_id=user_id, limit=limit, offset=offset, unread_only=unread_only
    )
    return {"total": total, "limit": limit, "offset": offset, "data": notifications}


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Marcar notificação como lida.**

    ### 📤 Retornos esperados
    * **`200 OK`**: Notificação marcada como lida.
    * **`404 NOT FOUND`**: Notificação não encontrada.
    """
    notification = await crud_notifications.get_notification(db, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return await crud_notifications.mark_as_read(db, notification=notification)
