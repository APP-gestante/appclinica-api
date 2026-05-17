# 🌙 Lunna (Gerar Vida) API

> **Acompanhamento Pré-natal de Excelência para Clínicas Privadas & Soluções White-label.**

A **Lunna API** é o coração tecnológico de um ecossistema mobile-first projetado para transformar a jornada do pré-natal. Focada em clínicas privadas, a plataforma oferece um acompanhamento clínico detalhado, seguro e humanizado para gestantes, médicos e equipes administrativas.

---

## 🚀 Visão Geral

O projeto foi concebido para ser uma solução **SaaS White-label**, permitindo que clínicas personalizem a experiência de suas pacientes enquanto mantêm um padrão rigoroso de gestão de dados clínicos.

### 👥 Perfis Suportados
* **🤰 Paciente (Gestante):** Monitoramento em tempo real da gravidez, registro de sinais vitais, visualização de exames e chat direto com a clínica.
* **🩺 Médico(a):** Gestão completa do prontuário eletrônico, acompanhamento de curvas de saúde (glicose, pressão) e controle de agenda.
* **📅 Secretária:** Operação logística, agendamentos, cadastros e comunicação institucional.
* **🔑 Administrador:** Controle global de clínicas, acessos e auditoria do sistema.

---

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
* **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/) (via SQLAlchemy 2.0 & AsyncPG)
* **Cache & Performance:** [Redis](https://redis.io/) (com expiração padrão de 5 minutos para otimização em clínicas)
* **Rate Limiting:** [SlowAPI](https://github.com/laurentS/slowapi) para segurança contra abusos
* **Migrações:** [Alembic](https://alembic.sqlalchemy.org/)
* **Containerização:** [Docker](https://www.docker.com/) & Docker Compose
* **Validação de Dados:** [Pydantic v2](https://docs.pydantic.dev/) com schemas autoexplicativos

---

## 📋 Principais Funcionalidades

### 🩺 Monitoramento Clínico
* **Sinais Vitais:** Registro e análise de Pressão Arterial, Glicemia e Controle de Contrações com detecção de alertas clínicos.
* **Evolução Gestacional:** Acompanhamento de peso, altura uterina e idade gestacional em semanas de forma dinâmica.
* **Exames:** Centralização de laudos técnicos de Ultrassons (USG), incluindo acompanhamento detalhado de parâmetros fetais.

### 🗓️ Gestão de Atendimento
* **Agendamentos:** Fluxo robusto de marcação, confirmação manual pela paciente e fluxo estruturado de solicitações e aprovação de remarcações.
* **Prontuário Digital:** Histórico clínico completo com classificação de risco.

---

## 📖 Documentação Técnica & Padrões da API

A documentação interativa da API foi totalmente revisada e está disponível localmente no endpoint `/docs`. Ela foi projetada para atuar como o guia único de integração para desenvolvedores web e mobile.

### 📌 Recursos Documentados no Swagger UI
* **Metadados Globais:** Introdução completa cobrindo as regras de segurança, matriz de permissões de perfis e tratamento de erros.
* **Organização Modular por Tags:**
  * `🔑 auth`: Login e controle de sessão stateless.
  * `👤 users`: Perfis de usuários, preferências e customização de marca (white-label).
  * `📅 appointments`: Fluxo de vida completo de agendamentos.
  * `🩸 vitals`: Lançamento e extração de séries temporais de sinais vitais para gráficos.
  * `🔬 exams`: Registro e consulta de laudos de exames (ultrassonografia).

### 🔒 Padrões de Segurança
* **Autenticação:** Toda rota protegida exige o cabeçalho:
  ```http
  Authorization: Bearer <seu_token_jwt>
  ```
* **Datas & Horários:** Todo tráfego de data e hora utiliza o padrão **ISO 8601** em UTC (ex: `YYYY-MM-DDTHH:MM:SSZ`).

---

## ⚙️ Como Executar

### Pré-requisitos
* Docker & Docker Compose instalados.

### Instalação e Execução

1. **Clonar o repositório:**
   ```bash
   git clone <repo-url>
   cd lunna-api
   ```

2. **Configurar variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env preenchendo as credenciais de banco e chaves de segurança
   ```

3. **Subir os containers:**
   ```bash
   docker-compose up -d --build
   ```

A API estará disponível em `http://localhost:8000`.  
A documentação interativa (Swagger) pode ser acessada em `http://localhost:8000/docs`.

### Validação de Sintaxe Local (Opcional)
Se precisar testar a integridade do código e dos schemas localmente no seu ambiente Python:
```bash
python -m py_compile main.py app/api/v1/*.py app/schemas/*.py
```

---

## 📂 Estrutura do Projeto

```text
├── app/
│   ├── api/          # Endpoints e Rotas versionadas (v1)
│   ├── core/         # Configurações globais, segurança e conexões
│   ├── models/       # Modelos SQLAlchemy para Supabase
│   └── schemas/      # Modelos Pydantic (DTOs com descrições e exemplos)
├── alembic/          # Migrações e versionamento do banco de dados
├── main.py           # Ponto de entrada e metadados globais da API
├── vercel.json       # Configuração para deploy serverless no Vercel
└── docker-compose.yml # Orquestração dos serviços locais (API e Redis)
```
