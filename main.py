from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1.router import api_router

# Configurar o Rate Limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectar ao Redis para cache
    redis_url = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    # Fechar conexões (opcional)

API_DESCRIPTION = """
# 🤰 Lunna API — Acompanhamento Pré-natal Premium

Bem-vinda(o) à documentação oficial da API da **Plataforma Lunna (Gerar Vida)**. Backend white-label para clínicas privadas de obstetrícia, com suporte completo ao app mobile React Native (GerarVida).

Stack: **FastAPI** · **PostgreSQL/Supabase** · **Redis** (cache + Pub/Sub) · **ARQ** (worker assíncrono) · **WebSocket** (chat em tempo real)

---

## 👥 Perfis de Acesso

| Role | Descrição | Acesso principal |
| :--- | :--- | :--- |
| **`patient`** | Paciente (gestante) | Prontuário, sinais vitais, exames, medicamentos, chat, notificações, nomes de bebê, desenvolvimento fetal |
| **`doctor`** | Médico(a) / Obstetra | Tudo do patient + prescrever exames/medicamentos + agenda + lista de pacientes |
| **`secretary`** | Secretária / Recepcionista | Dashboard da clínica + relatório diário + cadastrar pacientes + enviar lembretes |
| **`admin`** | Administrador da Clínica | Acesso total (equivalente a doctor + secretary) |
| **`superadmin`** | Administrador da Plataforma | Gerenciamento de clínicas (multi-tenant) |

---

## 🔒 Autenticação

Todos os recursos protegidos exigem JWT no header:
```http
Authorization: Bearer <access_token>
```

1. `POST /auth/login` → retorna `access_token` (24h) + `refresh_token` (7d)
2. Ao receber `401`, chame `POST /auth/refresh` com o `refresh_token` para obter novo `access_token` sem novo login
3. **WebSocket**: token vai no query param `?token=<jwt>` (browsers não suportam header em WS)

---

## ⚡ Features Principais

| Feature | Endpoint base | Notas |
| :--- | :--- | :--- |
| Chat em tempo real | `WS /patients/{id}/ws/chat` | Redis Pub/Sub; fallback HTTP em `POST /patients/{id}/messages` |
| Push Notifications | via worker ARQ | Expo Push API; requer `PATCH /users/{id}/push-token` após login |
| Lembretes agendados | `POST /patients/{id}/reminders` | Job ARQ com `_defer_until`; worker obrigatório |
| Nomes de bebê | `GET /baby-names` | 203 nomes com gênero, origem e trending |
| Desenvolvimento fetal | `GET /fetal-development/{week}` | Semanas 1–42; rota pública sem auth |

---

## 🛠️ Padrões de Resposta

* **Listas paginadas**: `{ total, limit, offset, data[] }`
* **Datas**: ISO 8601 — `YYYY-MM-DD` (date) · `YYYY-MM-DDTHH:MM:SSZ` (datetime UTC)
* **Erros**: `{ "detail": "mensagem" }`
* **Soft-delete**: registros deletados têm `deleted_at` preenchido e não aparecem em listagens

## ⚠️ Rate Limiting

Proteção ativa em endpoints sensíveis (login, registros). Retorna `HTTP 429 Too Many Requests` se excedido.
"""

openapi_tags = [
    # ── Autenticação ──────────────────────────────────────────────────────────
    {
        "name": "auth",
        "description": "🔑 **Autenticação & Controle de Sessão**. Login, logout e renovação de tokens JWT. O `access_token` expira em 24h; use `/auth/refresh` com o `refresh_token` (7d) para renová-lo sem novo login.",
    },
    # ── Perfis ────────────────────────────────────────────────────────────────
    {
        "name": "users",
        "description": "👤 **Usuários & Perfis**. CRUD de usuários, atualização de dados pessoais, registro de Expo push token (`push_token`) para notificações mobile e flag de onboarding concluído.",
    },
    {
        "name": "patients",
        "description": "🤰 **Pacientes, Médicos & Secretárias**. Cadastro de pacientes (por secretária), consulta de prontuário, lista de pacientes por médico, dashboards e agenda médica. Inclui rotas de secretária (`/secretary/dashboard`) e médico (`/doctors/{id}/agenda`).",
    },
    # ── Clínica ───────────────────────────────────────────────────────────────
    {
        "name": "announcements",
        "description": "📢 **Avisos da Clínica**. Listagem, criação, detalhe e marcação de leitura de avisos. O campo `is_new` indica avisos criados nos últimos 7 dias. Leituras são rastreadas por usuário em `user_announcement_reads`.",
    },
    # ── Agenda ────────────────────────────────────────────────────────────────
    {
        "name": "appointments",
        "description": "📅 **Consultas & Agendamentos**. Criação de consultas (por médico ou pelo `patient_id`), confirmação, solicitação/aprovação de remarcação, cancelamento e relatório diário da clínica (`GET /clinics/{id}/reports/daily`).",
    },
    # ── Sinais Vitais ─────────────────────────────────────────────────────────
    {
        "name": "vitals",
        "description": "🩸 **Sinais Vitais & Biometria**. Registro e monitoramento de Contrações, Glicemia e Pressão Arterial. Inclui endpoints de estatísticas agregadas e séries temporais para gráficos.",
    },
    # ── Exames ────────────────────────────────────────────────────────────────
    {
        "name": "exams",
        "description": "🔬 **Exames de Imagem, Vacinas & Laboratoriais**. Registro de ultrassonografias (USG), vacinas e exames laboratoriais (`lab_tests`). Escrita requer role `doctor` ou `admin`; leitura é aberta a qualquer usuário autenticado.\n\nValores válidos para `lab_test.type`: `hemograma` · `glicemia` · `urina` · `outros`\nValores válidos para `lab_test.status`: `pending` · `completed` · `abnormal`",
    },
    # ── Tratamentos ───────────────────────────────────────────────────────────
    {
        "name": "medications",
        "description": "💊 **Medicamentos & Prescrições**. Criação, listagem (com filtro `active?`) e atualização parcial de prescrições. Escrita requer role `doctor` ou `admin`.",
    },
    # ── Notificações & Lembretes ──────────────────────────────────────────────
    {
        "name": "notifications",
        "description": "🔔 **Notificações In-App**. Listagem com filtro `unread_only` e marcação de leitura individual. Notificações são criadas automaticamente pelo worker ARQ (`send_push_notification`) e também enviadas via Expo Push API se o usuário tiver `push_token` cadastrado.\n\nTipos: `appointment_reminder` · `clinic_announcement` · `vital_alert`",
    },
    {
        "name": "reminders",
        "description": "⏰ **Lembretes Agendados**. Criação de lembretes com `send_at` — o servidor enfileira um job ARQ com `_defer_until` que dispara o push no horário exato. Requer role `secretary` ou `admin`. O worker ARQ deve estar em execução.\n\nTipos: `appointment` · `exam` · `medication`",
    },
    # ── Chat ──────────────────────────────────────────────────────────────────
    {
        "name": "chat",
        "description": "💬 **Chat em Tempo Real**. Histórico via HTTP (`GET`) + envio via HTTP (`POST`, publica no Redis) + canal **WebSocket** em tempo real.\n\n**WebSocket:** `ws://<host>/api/v1/patients/{patient_id}/ws/chat?token=<jwt>`\n- JWT no query param (WS não suporta header Authorization)\n- Enviar: `{ \"content\": \"mensagem\" }`\n- Receber: objeto `MessageResponse` em JSON\n- Código de desconexão `4001` = token inválido — não reconectar\n\nArquitetura: FastAPI nativo + Redis Pub/Sub por conexão (canal `chat:{patient_id}`).",
    },
    # ── Conteúdo Estático ─────────────────────────────────────────────────────
    {
        "name": "baby-names",
        "description": "👶 **Nomes de Bebê**. Listagem com filtros `gender` e `search`, gerenciamento de favoritos por paciente. O campo `is_favorite` é preenchido automaticamente para usuários com role `patient`.\n\nGêneros: `male` · `female` · `neutral` · Tendências: `rising` · `stable` · `declining`",
    },
    {
        "name": "fetal-development",
        "description": "🫀 **Desenvolvimento Fetal**. Dados clínicos por semana gestacional (1–42): tamanho, peso, descrição e marcos de desenvolvimento (`highlights`). **Rota pública — não requer autenticação.** Dados pré-populados via seed (`python alembic/seeds/fetal_development.py`).",
    },
    # ── Administração ─────────────────────────────────────────────────────────
    {
        "name": "superadmin",
        "description": "🛡️ **Superadmin**. Gerenciamento de clínicas e configurações globais da plataforma. Requer role `superadmin`.",
    },
    {
        "name": "doctor",
        "description": "👨‍⚕️ **Rotas exclusivas de Médico**. Dashboard, agenda e lista de pacientes. Requer role `doctor` ou `admin`.",
    },
    {
        "name": "secretary",
        "description": "🗂️ **Rotas exclusivas de Secretária**. Dashboard da clínica e cadastro de pacientes. Requer role `secretary` ou `admin`.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=API_DESCRIPTION,
    version=settings.VERSION,
    openapi_tags=openapi_tags,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# Adicionar o Limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

import time
import logging

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lunna_api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"➡️ [REQ] {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Duracao: {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"❌ [ERRO] {request.method} {request.url.path} | "
            f"Mensagem: {str(e)} | Duracao: {process_time:.2f}ms",
            exc_info=True
        )
        raise e

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@limiter.limit("50/minute")
def root(request: Request):
    return {
        "message": "Welcome to Lunna API",
        "docs": "/docs",
        "version": settings.VERSION
    }

app.include_router(api_router, prefix=settings.API_V1_STR)
