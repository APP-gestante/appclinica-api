import asyncio
import json
from uuid import UUID
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi import status as http_status
from redis import asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.api.dependencies import get_db, get_current_user
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import ALGORITHM
from app.core.ws import manager
from app.crud import messages as crud_messages
from app.models.user import User
from app.models.enums import MessageSenderType
from app.schemas.messages import MessageCreate, MessageResponse, MessageListResponse

router = APIRouter()

_ROLE_TO_SENDER = {
    "patient": MessageSenderType.patient,
    "doctor": MessageSenderType.doctor,
    "secretary": MessageSenderType.secretary,
    "admin": MessageSenderType.doctor,
    "superadmin": MessageSenderType.doctor,
}


async def _validate_ws_token(token: str) -> User:
    """Decode JWT from query param and return the User (used for WebSocket auth)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
    except (jwt.PyJWTError, ValueError):
        raise WebSocketDisconnect(code=4001)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise WebSocketDisconnect(code=4001)

    return user


# ── HTTP endpoints ────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/messages", response_model=MessageListResponse)
async def list_messages(
    patient_id: UUID,
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    before_id: Optional[UUID] = Query(None, description="Cursor: buscar mensagens anteriores a este ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Histórico de mensagens do chat de uma paciente.**

    Retorna mensagens em ordem decrescente (mais recente primeiro). Use `before_id` para
    paginação por cursor ao carregar mensagens mais antigas.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada de mensagens.
    """
    total, msgs = await crud_messages.get_messages(
        db, patient_id=patient_id, limit=limit, offset=offset, before_id=before_id
    )
    return {"total": total, "limit": limit, "offset": offset, "data": msgs}


@router.post(
    "/patients/{patient_id}/messages",
    response_model=MessageResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def send_message(
    patient_id: UUID,
    obj_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Enviar mensagem no chat via HTTP (fallback).**

    Persiste a mensagem e publica no canal Redis para notificar conexões WebSocket abertas.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Mensagem criada e publicada no canal em tempo real.
    """
    sender_role = _ROLE_TO_SENDER.get(current_user.role, MessageSenderType.system)
    msg = await crud_messages.create_message(
        db,
        patient_id=patient_id,
        sender_id=current_user.id,
        sender_role=sender_role,
        content=obj_in.content,
    )

    redis_url = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    redis = aioredis.from_url(redis_url)
    try:
        payload = MessageResponse.model_validate(msg).model_dump_json()
        await redis.publish(f"chat:{patient_id}", payload)
    finally:
        await redis.close()

    return msg


@router.patch("/patients/{patient_id}/messages/read", status_code=http_status.HTTP_204_NO_CONTENT)
async def mark_messages_read(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Marcar todas as mensagens do chat como lidas.**

    ### 📤 Retornos esperados
    * **`204 NO CONTENT`**: Mensagens marcadas como lidas.
    """
    await crud_messages.mark_all_read(db, patient_id=patient_id)


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/patients/{patient_id}/ws/chat")
async def chat_ws(
    websocket: WebSocket,
    patient_id: UUID,
    token: str = Query(..., description="Access token JWT"),
):
    """
    **Canal de chat em tempo real via WebSocket.**

    Protocolo:
    - Conectar: `ws://<host>/api/v1/patients/{patient_id}/ws/chat?token=<access_token>`
    - Enviar:   `{ "content": "Olá Dra." }`
    - Receber:  JSON com campos `id`, `patient_id`, `sender_id`, `sender_role`, `content`, `read`, `created_at`

    O token JWT deve ser passado via query param (WebSocket não suporta header Authorization).
    """
    try:
        user = await _validate_ws_token(token)
    except WebSocketDisconnect:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, str(patient_id))

    redis_url = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    redis_sub = aioredis.from_url(redis_url)
    redis_pub = aioredis.from_url(redis_url)
    pubsub = redis_sub.pubsub()
    await pubsub.subscribe(f"chat:{patient_id}")

    async def listen_redis():
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    await websocket.send_text(msg["data"])
                except Exception:
                    break

    redis_task = asyncio.create_task(listen_redis())

    try:
        sender_role = _ROLE_TO_SENDER.get(user.role, MessageSenderType.system)

        while True:
            data = await websocket.receive_json()
            content = str(data.get("content", "")).strip()
            if not content:
                continue

            async with AsyncSessionLocal() as db:
                msg = await crud_messages.create_message(
                    db,
                    patient_id=patient_id,
                    sender_id=user.id,
                    sender_role=sender_role,
                    content=content,
                )
                payload = MessageResponse.model_validate(msg).model_dump_json()

            await redis_pub.publish(f"chat:{patient_id}", payload)

    except (WebSocketDisconnect, Exception):
        pass
    finally:
        redis_task.cancel()
        manager.disconnect(websocket, str(patient_id))
        await pubsub.unsubscribe(f"chat:{patient_id}")
        await redis_sub.close()
        await redis_pub.close()
