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

# Background worker (ARQ)
arq app.worker.WorkerSettings

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "describe the change"
alembic downgrade -1
```

## Architecture

### Request Lifecycle
`main.py` → `app/api/v1/router.py` → endpoint module → `app/api/dependencies.py` (auth) → `app/crud/` → async SQLAlchemy session → PostgreSQL

### Core Layers

- **`app/core/config.py`** — Pydantic `Settings` loaded from `.env`. `DATABASE_URL` takes precedence over individual `POSTGRES_*` vars; same pattern for `REDIS_URL` vs `REDIS_HOST/PORT`. The `sqlalchemy_database_uri` property auto-converts `postgresql://` to `postgresql+asyncpg://`.
- **`app/core/database.py`** — Async SQLAlchemy engine with `ssl: "require"` (Supabase). `AsyncSessionLocal` is the session factory.
- **`app/core/security.py`** — JWT (HS256) `create_access_token` / `create_refresh_token`, bcrypt password hashing.
- **`app/api/dependencies.py`** — Three key FastAPI dependencies: `get_db` (yields session), `get_current_user` (decodes JWT, loads User), `require_role(["doctor", "admin"])` (RBAC guard).

### Models

All models inherit from `app/models/base.py::BaseModel` which provides UUID PK, `created_at`, `updated_at`, and `deleted_at` (soft-delete pattern — not enforced in queries automatically).

User has three polymorphic sub-profiles linked by `user_id`:
- `Patient` — gestational data (LMP, EDD, risk level, vitals history)
- `Doctor` — CRM, specialty
- `Secretary` — position

### Roles & RBAC

Defined in `app/models/enums.py::UserRole`: `patient`, `doctor`, `secretary`, `admin`. Enforce with `Depends(require_role(["doctor"]))` in route definitions.

### Schemas vs Models

`app/schemas/` holds Pydantic v2 DTOs (request/response). Always use `model_dump(exclude_unset=True)` when applying partial updates so only provided fields are written.

### Background Jobs

`app/worker.py` uses **ARQ** (async Redis queue). Add new tasks by defining `async def my_task(ctx, ...)` and registering in `WorkerSettings.functions`. Enqueue from endpoints via `await redis.enqueue_job("my_task", ...)`.

### Caching

**fastapi-cache2** with Redis backend initialized in `main.py` lifespan. Decorate read endpoints with `@cache(expire=60)`.

## Environment Setup

Copy `.env.example` to `.env`. Minimum required for local dev without Docker:

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/lunna
REDIS_URL=redis://localhost:6379
SECRET_KEY=<any-long-random-string>
```

## Deployment

The API deploys to **Vercel** via `vercel.json` (routes everything through `main.py`). Docker Compose is for local dev — the compose file does not include a PostgreSQL service (database is expected on Supabase).

## Key Gotchas

- `alembic/env.py` uses `connect_args={"ssl": "require"}` — running migrations locally against a non-SSL DB will fail. Override by editing `env.py` temporarily or use `DATABASE_URL` pointing to a local non-SSL instance.
- `tests/conftest.py` imports from `app.core.dependencies` but the actual module is `app.api.dependencies` — tests may need this fixed before running.
- Access token TTL defaults to 1440 minutes (24h); refresh token is hardcoded to 7 days in `security.py`.
