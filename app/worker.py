import asyncio
import httpx
from uuid import UUID
from arq import Worker
from app.core.config import settings
from app.core.database import AsyncSessionLocal


async def send_email_task(ctx, email: str, subject: str, body: str):
    print(f"Simulando envio de email para {email}...")
    await asyncio.sleep(2)
    print(f"Email '{subject}' enviado com sucesso para {email}!")


async def generate_report_task(ctx, clinic_id: str):
    print(f"Gerando relatório pesado para a clínica {clinic_id}...")
    await asyncio.sleep(5)
    print("Relatório finalizado!")


async def send_push_notification(
    ctx,
    user_id: str,
    title: str,
    body: str,
    data: dict = None,
    notification_type: str = "vital_alert",
):
    """Persiste Notification no banco e dispara Expo Push se push_token disponível."""
    from sqlalchemy import select
    from app.models.user import User
    from app.models.notifications import Notification
    from app.models.enums import NotificationType

    async with AsyncSessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.id == UUID(user_id)))
        ).scalar_one_or_none()
        if not user:
            return

        ntype = NotificationType(notification_type) if notification_type in NotificationType._value2member_map_ else NotificationType.vital_alert
        notification = Notification(
            user_id=UUID(user_id),
            type=ntype,
            title=title,
            body=body,
            data=data,
        )
        db.add(notification)
        await db.commit()

        if user.push_token:
            payload = {"to": user.push_token, "title": title, "body": body}
            if data:
                payload["data"] = data
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        "https://exp.host/--/api/v2/push/send",
                        json=payload,
                        timeout=10.0,
                    )
                except httpx.HTTPError as exc:
                    print(f"Expo push failed for user {user_id}: {exc}")


async def send_reminder(ctx, reminder_id: str):
    """Executa o lembrete agendado: busca paciente, dispara push e marca como enviado."""
    from sqlalchemy import select
    from app.models.reminders import Reminder
    from app.models.user import Patient, User

    async with AsyncSessionLocal() as db:
        reminder = (
            await db.execute(
                select(Reminder).where(Reminder.id == UUID(reminder_id))
            )
        ).scalar_one_or_none()
        if not reminder or reminder.sent_at is not None:
            return

        patient = (
            await db.execute(
                select(Patient).where(Patient.id == reminder.patient_id)
            )
        ).scalar_one_or_none()
        if not patient:
            return

        user = (
            await db.execute(select(User).where(User.id == patient.user_id))
        ).scalar_one_or_none()
        if not user:
            return

        await send_push_notification(
            ctx,
            user_id=str(user.id),
            title="Lembrete",
            body=reminder.message,
            data={"reminder_id": reminder_id, "type": reminder.type.value},
            notification_type="appointment_reminder",
        )

        from datetime import datetime, timezone
        reminder.sent_at = datetime.now(timezone.utc)
        db.add(reminder)
        await db.commit()


class WorkerSettings:
    """
    Configurações do Worker ARQ.
    Para rodar os workers: arq app.worker.WorkerSettings
    """
    functions = [send_email_task, generate_report_task, send_push_notification, send_reminder]
    redis_settings = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

    async def on_startup(ctx):
        print("Worker iniciado e conectado ao Redis!")

    async def on_shutdown(ctx):
        print("Worker desligado.")
