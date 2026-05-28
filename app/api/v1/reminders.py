from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from arq import ArqRedis

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.crud import reminders as crud_reminders
from app.crud import patient as crud_patient
from app.schemas.reminders import ReminderCreate, ReminderResponse
from app.core.config import settings

router = APIRouter()


async def get_arq_redis() -> ArqRedis:
    from arq import create_pool
    from arq.connections import RedisSettings
    redis_url = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    return await create_pool(RedisSettings.from_dsn(redis_url))


@router.post(
    "/patients/{patient_id}/reminders",
    response_model=ReminderResponse,
    status_code=201,
    dependencies=[Depends(require_role(["secretary", "admin"]))],
)
async def create_reminder(
    patient_id: UUID,
    obj_in: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Agendar lembrete para um paciente.**

    O lembrete é persistido e um job ARQ é enfileirado para disparar a push notification
    no horário especificado em `send_at`.

    ### 📌 Requisitos de Segurança
    * Requer `Authorization: Bearer <token>` com role `secretary` ou `admin`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Lembrete criado e job agendado.
    * **`404 NOT FOUND`**: Paciente não encontrado.
    """
    patient = await crud_patient.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    reminder = await crud_reminders.create_reminder(
        db, obj_in=obj_in, patient_id=patient_id, created_by=current_user.id
    )

    arq = await get_arq_redis()
    try:
        await arq.enqueue_job(
            "send_reminder",
            str(reminder.id),
            _defer_until=obj_in.send_at,
        )
    finally:
        await arq.aclose()

    return reminder
