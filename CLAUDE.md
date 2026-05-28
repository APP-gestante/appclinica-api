# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Lunna API** — a prenatal monitoring SaaS white-label backend for private obstetrics clinics. Patients (gestantes), doctors, secretaries, and admins each have distinct roles and permissions.

## Commands

```bash
# Run dev server
uvicorn main:app --reload

# Run with Docker (Redis + API)
docker-compose up -d --build

# Run all tests (requires local PostgreSQL at localhost:5432/appclinica_test)
pytest

# Run a single test
pytest tests/test_auth.py::test_login_success -v

# Background worker (ARQ) — required for push notifications and reminders
arq app.worker.WorkerSettings

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "describe the change"
alembic downgrade -1

# Populate static data (run once after alembic upgrade head)
python alembic/seeds/baby_names.py
python alembic/seeds/fetal_development.py

# Syntax check all API files quickly
python -m py_compile main.py app/api/v1/*.py app/models/*.py app/crud/*.py
```

## Architecture

### Request Lifecycle
`main.py` → `app/api/v1/router.py` → endpoint module → `app/api/dependencies.py` (auth) → `app/crud/` → async SQLAlchemy session → PostgreSQL

WebSocket path: `app/api/v1/messages.py` → JWT validated via query param → `app/core/ws.py` (ConnectionManager) + Redis Pub/Sub

### Core Layers

- **`app/core/config.py`** — Pydantic `Settings` loaded from `.env`. `DATABASE_URL` takes precedence over individual `POSTGRES_*` vars; same pattern for `REDIS_URL` vs `REDIS_HOST/PORT`. The `sqlalchemy_database_uri` property auto-converts `postgresql://` to `postgresql+asyncpg://`.
- **`app/core/database.py`** — Async SQLAlchemy engine with `ssl: "require"` (Supabase). `AsyncSessionLocal` is the session factory — also used directly in ARQ worker tasks.
- **`app/core/security.py`** — JWT (HS256) `create_access_token` / `create_refresh_token`, bcrypt password hashing. `ALGORITHM = "HS256"`.
- **`app/core/ws.py`** — `ConnectionManager` singleton. Tracks open WebSocket connections keyed by `patient_id`. Call `manager.connect()`, `manager.disconnect()`, `manager.broadcast()`. Each WS connection creates its own Redis Pub/Sub subscription to `chat:{patient_id}`.
- **`app/api/dependencies.py`** — Three key FastAPI dependencies: `get_db` (yields session), `get_current_user` (decodes JWT, loads User), `require_role(["doctor", "admin"])` (RBAC guard).

### Models

All models inherit from `app/models/base.py::BaseModel` which provides UUID PK, `created_at`, `updated_at`, and `deleted_at` (soft-delete — **not enforced automatically**; every query must add `.where(Model.deleted_at.is_(None))`).

**Current models:**

| Model | Table | Notes |
|---|---|---|
| `User` | `users` | Base profile; has `push_token`, `onboarding_completed` |
| `Patient` | `patients` | Linked to `User` via `user_id`; gestational data |
| `Doctor` | `doctors` | Linked to `User` via `user_id` |
| `Secretary` | `secretaries` | Linked to `User` via `user_id` |
| `Appointment` | `appointments` | — |
| `Contraction` | `contractions` | — |
| `GlucoseReading` | `glucose_readings` | — |
| `BloodPressureReading` | `blood_pressure_readings` | — |
| `Ultrasound` | `ultrasounds` | — |
| `Vaccine` | `vaccines` | — |
| `Announcement` | `announcements` | — |
| `UserAnnouncementRead` | `user_announcement_reads` | Pivot; UniqueConstraint(user_id, announcement_id) |
| `LabTest` | `lab_tests` | Enums: `LabTestType`, `LabTestStatus` |
| `Medication` | `medications` | — |
| `Notification` | `notifications` | JSON `data` column; dispatched by ARQ worker |
| `Reminder` | `reminders` | `send_at` triggers deferred ARQ job |
| `BabyName` | `baby_names` | Static seed data; `popularity_score`, `trend` |
| `PatientBabyNameFavorite` | `patient_baby_name_favorites` | Pivot; UniqueConstraint(patient_id, baby_name_id) |
| `FetalDevelopment` | `fetal_development` | Static seed; one row per gestational week (1–42) |
| `Message` | `messages` | Chat messages; published to Redis on create |

### Enums (`app/models/enums.py`)

`UserRole`, `AppointmentStatus`, `AppointmentType`, `RiskLevel`, `VitalClassification`, `TimeOfDay`, `GlucoseMoment`, `FetalPresentation`, `UltrasoundType`, `VaccineStatus`, `SerologyStatus`, `AnnouncementCategory`, `MessageSenderType`, `LabTestType`, `LabTestStatus`, `NotificationType`, `ReminderType`, `BabyNameGender`, `NameTrend`

### Roles & RBAC

Defined in `UserRole`: `patient`, `doctor`, `secretary`, `admin`, `superadmin`. Enforce with `Depends(require_role(["doctor"]))` in route definitions.

`superadmin` é o único role sem `clinic_id` — a coluna é nullable exatamente por isso (migration `f1a2b3c4d5e6`). `UserResponse.clinic_id` é `Optional[UUID]`.

### Schemas vs Models

`app/schemas/` holds Pydantic v2 DTOs. Base classes in `app/schemas/base.py`:
- `CoreModel` — base with `from_attributes=True`
- `BaseEntitySchema(CoreModel)` — adds `id`, `created_at`, `updated_at`, `deleted_at`

Always use `model_dump(exclude_unset=True)` when applying partial updates.

### Background Jobs (ARQ Worker)

`app/worker.py` — tasks registered in `WorkerSettings.functions`:

| Task | Trigger | What it does |
|---|---|---|
| `send_push_notification` | Enqueued by any code | Saves `Notification` to DB, calls Expo Push API via `httpx` |
| `send_reminder` | Enqueued with `_defer_until=send_at` | Resolves patient → user → calls `send_push_notification`, marks `sent_at` |
| `send_email_task` | Manual | Placeholder email task |
| `generate_report_task` | Manual | Placeholder report task |

Enqueue from an endpoint:
```python
from arq import create_pool
from arq.connections import RedisSettings
redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
await redis.enqueue_job("send_push_notification", str(user_id), title, body)
```

### WebSocket Chat

`WS /api/v1/patients/{patient_id}/ws/chat?token=<jwt>`

- JWT goes in **query param** (browsers/WS clients don't support Authorization headers)
- Each connection subscribes to Redis channel `chat:{patient_id}`
- Inbound WS message → save to DB → `redis.publish(f"chat:{patient_id}", payload)`
- Redis listener task forwards published messages back to all open WS connections for that patient
- Disconnect code `4001` = invalid/expired token

### Static Seeds

```
alembic/seeds/baby_names.py        — 203 names (female/male/neutral), idempotent
alembic/seeds/fetal_development.py — weeks 1–42, idempotent
```

Both scripts are idempotent (skip if data already exists) and use `asyncio.run()` with `AsyncSessionLocal`.

### Caching

**fastapi-cache2** with Redis backend initialized in `main.py` lifespan. Decorate read endpoints with `@cache(expire=60)`. Currently cached: `GET /users/{id}/clinic` (300s).

### Migration Pattern

All new enum types use the safe creation pattern:
```sql
DO $$ BEGIN
    CREATE TYPE myenum AS ENUM ('a', 'b');
EXCEPTION WHEN duplicate_object THEN null; END $$;
```

Pass `create_type=False` to `postgresql.ENUM(...)` in the migration file.

## Environment Setup

Minimum required for local dev:

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/lunna
REDIS_URL=redis://localhost:6379
SECRET_KEY=<any-long-random-string>
```

### Supabase (produção / staging)

Usar o **session pooler** (`aws-1-sa-east-1.pooler.supabase.com:5432`), não a conexão direta (`db.<ref>.supabase.co:5432`).

- A conexão direta resolve para IPv6 em algumas redes, causando timeout silencioso.
- O transaction pooler (porta 6543) é incompatível com asyncpg (prepared statements). Usar porta 5432 do session pooler.
- Senha com `@` deve ser URL-encoded: `@` → `%40` na DATABASE_URL.

```
DATABASE_URL=postgresql+asyncpg://postgres.<ref>:%40SuaSenha@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
```

### Python version

asyncpg não tem wheel para Python 3.14+. Usar **Python 3.12**:

```bash
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Deployment

The API deploys to **Vercel** via `vercel.json`. Docker Compose is for local dev — no PostgreSQL container (database lives on Supabase).

The ARQ worker must run as a **separate process** — Vercel serverless does not support long-running processes. Deploy the worker on Railway, Render, or a VPS alongside the API.

## Key Gotchas

- **Alembic SSL**: `alembic/env.py` uses `connect_args={"ssl": "require"}` — running migrations locally against a non-SSL DB will fail. Edit `env.py` temporarily or point `DATABASE_URL` at a local non-SSL instance.
- **`%` na DATABASE_URL com Alembic:** `alembic/env.py` passa a URL via `configparser`, que interpreta `%` como sintaxe de interpolação. A linha que seta a URL deve fazer `.replace("%", "%%")`:
  ```python
  config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_uri.replace("%", "%%"))
  ```
- **Múltiplos heads no Alembic:** se houver dois branches de migração, `alembic upgrade head` falha. Usar `alembic upgrade heads` (plural) ou criar migration de merge com `down_revision` como tupla.
- **Tests import path**: `tests/conftest.py` imports from `app.core.dependencies` but the actual module is `app.api.dependencies` — fix before running tests.
- **Token TTL**: access token expires in 1440 min (24h); refresh token in 7 days (hardcoded in `security.py`).
- **WebSocket JWT**: WS connections cannot send `Authorization` header — token must go in `?token=<jwt>` query param. Validate with `jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])` directly, not via `Depends(get_current_user)`.
- **Worker required for push/reminders**: `send_push_notification` and `send_reminder` only execute if `arq app.worker.WorkerSettings` is running. Reminders use `_defer_until` — the job sits in Redis until `send_at` is reached.
- **Soft-delete not automatic**: every CRUD query must explicitly add `.where(Model.deleted_at.is_(None))`.
- **UUID serialization in ARQ**: pass UUIDs as `str()` in job arguments — ARQ serializes via JSON which doesn't handle UUID natively.
- **`admin` role in MessageSenderType**: `MessageSenderType` has `patient | doctor | secretary | system` — `admin` role maps to `doctor` in the messages endpoint.
- **Seed superadmin**: `seed.py` cria o usuário `superadmin@lunna.app` (role `superadmin`, `clinic_id=None`). Deve existir antes de usar o dashboard `/superadmin` no frontend.
