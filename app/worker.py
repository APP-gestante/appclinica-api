import asyncio
from arq import Worker
from app.core.config import settings

async def send_email_task(ctx, email: str, subject: str, body: str):
    """
    Exemplo de tarefa de background (Background Job).
    Na vida real isso enviaria um e-mail.
    """
    print(f"Simulando envio de email para {email}...")
    await asyncio.sleep(2)  # simula delay da rede
    print(f"Email '{subject}' enviado com sucesso para {email}!")

async def generate_report_task(ctx, clinic_id: str):
    """
    Exemplo de tarefa pesada (Relatório Mensal).
    """
    print(f"Gerando relatório pesado para a clínica {clinic_id}...")
    await asyncio.sleep(5)
    print("Relatório finalizado!")

class WorkerSettings:
    """
    Configurações do Worker ARQ.
    Para rodar os workers: arq app.worker.WorkerSettings
    """
    functions = [send_email_task, generate_report_task]
    redis_settings = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    
    # Executado ao ligar o worker
    async def on_startup(ctx):
        print("Worker iniciado e conectado ao Redis!")

    # Executado ao desligar o worker
    async def on_shutdown(ctx):
        print("Worker desligado.")
