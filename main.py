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

Bem-vinda(o) à documentação oficial da API da **Plataforma Lunna (Gerar Vida)**. Esta API RESTful fornece toda a infraestrutura de backend para o aplicativo móvel white-label de acompanhamento pré-natal, projetado sob medida para gestantes atendidas em clínicas privadas de obstetrícia.

A API foi desenvolvida utilizando **FastAPI** para alta performance e validação robusta de tipos, integrada ao **Supabase (PostgreSQL)** para persistência resiliente, **Redis** para cache de respostas e controle de sessões, e **SlowAPI** para proteção contra abusos de taxa (rate limiting).

---

## 👥 Perfis de Acesso & Matriz de Permissões

A plataforma suporta 4 níveis distintos de acesso (`roles`), cada um com responsabilidades e permissões específicas:

| Nível de Acesso | Descrição Funcional | Permissões Principais |
| :--- | :--- | :--- |
| **`patient`** | **Paciente (Gestante)** | Visualizar o próprio prontuário, registrar sinais vitais, confirmar agendamentos de consultas e acompanhar estatísticas de gestação. |
| **`doctor`** | **Médico(a) / Obstetra** | Acompanhar a evolução clínica das pacientes sob seus cuidados, atualizar prontuários, prescrever exames, gerenciar sua própria agenda de consultas. |
| **`secretary`** | **Secretária / Recepcionista** | Gerenciar o agendamento de consultas de todos os médicos da clínica, cadastrar novas pacientes, gerenciar informações de contato e enviar lembretes. |
| **`admin`** | **Administrador da Clínica** | Configuração do ambiente SaaS white-label (logo, cores da marca), gerenciamento da equipe (médicos e secretárias), auditoria e configurações gerais. |

---

## 🔒 Segurança & Autenticação

Todos os recursos protegidos da API exigem autenticação via token JWT (JSON Web Token) no formato **Bearer Token**.

### Passos para Autenticação:
1. Envie uma requisição `POST /api/v1/auth/login` com email e senha.
2. O servidor retornará um `access_token` (de curta duração) e um `refresh_token` (de longa duração).
3. Inclua o token de acesso em todas as chamadas subsequentes no cabeçalho HTTP:
   ```http
   Authorization: Bearer <seu_access_token>
   ```

---

## ⚡ Performance, Caching & Limites

Para garantir a melhor experiência móvel e segurança contra negação de serviço:
* **Cache Inteligente**: Endpoints de leitura estática ou de baixa variação (como informações da clínica ou históricos de exames consolidados) utilizam cache no **Redis** com expiração automática.
* **Rate Limiting (Limite de Taxa)**: Proteção ativa nos endpoints sensíveis (como Login e registros repetitivos) para evitar abusos de requisições. Se excedido, a API retornará o status `HTTP 429 Too Many Requests`.

---

## 🛠️ Padrões de Resposta & Erros

* **Datas e Horas**: Seguem estritamente o padrão **ISO 8601** (exemplo: `YYYY-MM-DD` para datas e `YYYY-MM-DDTHH:MM:SSZ` para carimbos de data/hora UTC).
* **Erros Padronizados**: Respostas de erro retornam com o formato JSON apropriado:
  ```json
  {
    "detail": "Mensagem detalhada sobre o erro ocorrido."
  }
  ```
"""

openapi_tags = [
    {
        "name": "auth",
        "description": "🔑 **Autenticação & Controle de Sessão**. Endpoints para login, logout e gerenciamento de tokens JWT (JSON Web Tokens).",
    },
    {
        "name": "users",
        "description": "👤 **Gerenciamento de Usuários & Perfis**. Cadastro de usuários, atualização de dados pessoais, preferências de notificação/tema e recuperação de informações da clínica associada.",
    },
    {
        "name": "appointments",
        "description": "📅 **Consultas & Agendamentos**. Criação de consultas, confirmação de presença pela paciente, solicitação de remarcação, aprovação de remarcação pela clínica, cancelamento e visualização de agendas médicas.",
    },
    {
        "name": "vitals",
        "description": "🩸 **Sinais Vitais & Biometria**. Registro e monitoramento de sinais vitais essenciais para gestantes (Glicose, Pressão Arterial e Contrações), com endpoints de estatísticas e dados para gráficos.",
    },
    {
        "name": "exams",
        "description": "🔬 **Exames & Laudos Clínicos**. Gerenciamento de exames clínicos, focando no registro e acompanhamento de ultrassonografias (USG) obstétricas.",
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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {
        "message": "Welcome to Gerar Vida API",
        "docs": "/docs",
        "version": settings.VERSION
    }

app.include_router(api_router, prefix=settings.API_V1_STR)
