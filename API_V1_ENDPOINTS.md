# API v1 — Endpoints Implementados

Referência das rotas criadas ou convertidas de mock para dados reais na v1, mapeadas às telas do app mobile **GerarVida** (`lunna-app/GerarVida`).

Base URL: `http://<host>/api/v1`

---

## Autenticação

Todas as rotas protegidas exigem o header:
```
Authorization: Bearer <access_token>
```

O `access_token` expira em **24 horas**. Use o endpoint de refresh antes da expiração para obter um novo sem solicitar login novamente.

---

## Grupo 1 — Auth

### `POST /auth/login`

Autentica o usuário e retorna o par de tokens.

**Tela mobile:** `LoginScreen`

**Body:**
```json
{ "email": "maria@clinic.com", "password": "senha123" }
```

**Resposta 200:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "<uuid>",
    "name": "Maria da Silva",
    "email": "maria@clinic.com",
    "role": "patient",
    "clinic_id": "<uuid>",
    "is_active": true
  }
}
```

---

### `POST /auth/refresh` ✨ novo

Renova o `access_token` sem nova autenticação. O app armazena o `refresh_token` em `AsyncStorage` sob a chave `gv_refresh_token` e deve chamar este endpoint quando receber `401` de qualquer rota protegida.

**Tela mobile:** interceptor global de requisições (`src/services/api.ts`)

**Body:**
```json
{ "refresh_token": "<jwt>" }
```

**Resposta 200:**
```json
{ "access_token": "<novo_jwt>", "token_type": "bearer" }
```

**Erros:**
- `401` — token inválido, expirado ou não é do tipo `refresh`

---

### `POST /auth/logout`

Endpoint de sinalização. O app deve descartar os tokens locais ao receber `200`.

**Tela mobile:** menu de perfil / botão "Sair"

**Resposta 200:**
```json
{ "message": "Logged out successfully" }
```

---

## Grupo 2 — Paciente

### `GET /patients/{patient_id}` ✨ novo

Retorna dados gestacionais completos da paciente: semana atual, DUM, DPP, risco, dados do usuário.

**Tela mobile:** `HomeScreen` — elimina o hardcode "semana 24"

**Resposta 200:**
```json
{
  "id": "<uuid>",
  "user_id": "<uuid>",
  "prontuario": "PR-98765",
  "lmp_date": "2023-11-01",
  "edd": "2024-08-07",
  "current_week": 24,
  "risk_level": "low",
  "hospital": "Maternidade Santa Joana",
  "blood_type": "O+",
  "height_cm": "165",
  "weight_initial_kg": "62.5",
  "user": {
    "id": "<uuid>",
    "name": "Maria da Silva",
    "email": "maria@clinic.com",
    "phone": "(11) 99999-9999",
    "role": "patient"
  }
}
```

**Erros:**
- `404` — paciente não encontrada

---

## Grupo 3 — Prontuário

### `GET /patients/{patient_id}/prontuario` ✨ novo

Agrega dados clínicos (`Patient`) e cadastrais (`User`) em uma única resposta para o prontuário completo.

**Tela mobile:** `ProntuarioScreen` (paciente) e `PacienteDetalheScreen` (médico)

**Resposta 200:**
```json
{
  "patient_id": "<uuid>",
  "dados_clinicos": {
    "prontuario": "PR-98765",
    "lmp_date": "2023-11-01",
    "edd": "2024-08-07",
    "current_week": 24,
    "risk_level": "low",
    "doctor_id": "<uuid>",
    "blood_type": "O+",
    "height_cm": "165",
    "weight_initial_kg": "62.5",
    "imc": "22.9",
    "acompanhante": "João da Silva",
    "hospital": "Maternidade Santa Joana",
    "number_of_fetuses": 1,
    "parity": "G1P0",
    "cesarean_predicted": false
  },
  "user": {
    "id": "<uuid>",
    "name": "Maria da Silva",
    "email": "maria@clinic.com",
    "phone": "(11) 99999-9999"
  },
  "updated_at": "2024-03-15"
}
```

---

### `PUT /patients/{patient_id}/prontuario` ✨ novo

Atualiza campos editáveis do prontuário. Apenas os campos enviados no body são alterados (partial update).

**Tela mobile:** formulário de edição do prontuário

**Body (todos opcionais):**
```json
{
  "height_cm": "166",
  "weight_initial_kg": "63.0",
  "imc": "22.9",
  "blood_type": "A+",
  "acompanhante": "João da Silva",
  "hospital": "Maternidade Santa Joana",
  "risk_level": "low",
  "number_of_fetuses": 1,
  "parity": "G1P0",
  "cesarean_predicted": false
}
```

**Resposta 200:** objeto `PatientResponse` atualizado

**Erros:**
- `404` — paciente não encontrada

---

## Grupo 4 — Sinais Vitais (Contrações)

Prefixo montado pelo router: `/patients/{patient_id}/...`

### `POST /patients/{patient_id}/contractions`

Registra uma nova contração.

**Tela mobile:** `ContracoesScreen` — botão "Iniciar Contração"

**Body:**
```json
{
  "duration_seconds": 45,
  "interval_minutes": 7.5,
  "session_date": "2024-03-15"
}
```

**Resposta 201:** objeto `ContractionResponse` com `id`, timestamps e campos enviados

---

### `GET /patients/{patient_id}/contractions`

Lista histórico paginado de contrações.

**Query params:** `limit` (padrão 50, máx 100), `offset` (padrão 0)

**Resposta 200:**
```json
{ "total": 12, "limit": 50, "offset": 0, "data": [ /* ContractionResponse[] */ ] }
```

---

### `GET /patients/{patient_id}/contractions/stats` ✨ convertido de mock

Estatísticas agregadas calculadas sobre dados reais do banco.

**Tela mobile:** card de resumo em `ContracoesScreen`

**Resposta 200:**
```json
{
  "patient_id": "<uuid>",
  "total_contractions": 12,
  "average_duration_seconds": 45.0,
  "average_interval_minutes": 7.5
}
```

---

### `DELETE /patients/{patient_id}/contractions/session` ✨ convertido de mock

Limpa (soft-delete) todas as contrações do dia corrente.

**Tela mobile:** botão "Nova Sessão" / "Reiniciar"

**Resposta:** `204 No Content`

---

## Grupo 5 — Sinais Vitais (Glicose)

### `POST /patients/{patient_id}/glucose-readings`

Registra nova leitura de glicemia.

**Tela mobile:** `GlicoseScreen` — formulário de registro

**Body:**
```json
{
  "value_mg_dl": 95.0,
  "moment": "fasting",
  "classification": "normal",
  "notes": "Em jejum de 8h"
}
```

Valores válidos para `moment`: `fasting`, `after_meal`, `random`  
Valores válidos para `classification`: `normal`, `attention`, `high`

**Resposta 201:** objeto `GlucoseReadingResponse`

---

### `GET /patients/{patient_id}/glucose-readings`

Lista histórico paginado de leituras de glicose.

**Query params:** `limit`, `offset`

**Resposta 200:**
```json
{ "total": 30, "limit": 50, "offset": 0, "data": [ /* GlucoseReadingResponse[] */ ] }
```

---

### `GET /patients/{patient_id}/glucose-readings/stats` ✨ convertido de mock

Estatísticas agregadas sobre dados reais.

**Tela mobile:** card de resumo em `GlicoseScreen`

**Resposta 200:**
```json
{
  "patient_id": "<uuid>",
  "total_readings": 30,
  "average": 92.4,
  "min": 72.0,
  "max": 130.0,
  "last_reading": {
    "value_mg_dl": 88.0,
    "moment": "fasting",
    "classification": "normal",
    "timestamp": "2024-03-15T08:00:00"
  }
}
```

---

### `GET /patients/{patient_id}/glucose-readings/chart` ✨ convertido de mock

Série temporal para renderização do gráfico de linha.

**Tela mobile:** gráfico em `GlicoseScreen`

**Query params:** `days` (padrão 30, máx 365)

**Resposta 200:**
```json
{
  "data": [
    { "timestamp": "2024-02-14T08:00:00", "value": 88.0, "moment": "fasting" }
  ],
  "normal_limit": 95,
  "hypertension_limit": 126
}
```

---

## Grupo 6 — Sinais Vitais (Pressão Arterial)

### `POST /patients/{patient_id}/blood-pressure`

Registra nova leitura de pressão arterial.

**Tela mobile:** `PressaoScreen` — formulário de registro

**Body:**
```json
{
  "systolic": 120,
  "diastolic": 80,
  "pulse_bpm": 72,
  "moment": "morning",
  "classification": "normal"
}
```

Valores válidos para `moment`: `morning`, `afternoon`, `evening`, `night`  
Valores válidos para `classification`: `normal`, `attention`, `high`

**Resposta 201:** objeto `BloodPressureResponse`

---

### `GET /patients/{patient_id}/blood-pressure`

Lista histórico paginado de leituras de pressão.

**Query params:** `limit`, `offset`

**Resposta 200:**
```json
{ "total": 20, "limit": 50, "offset": 0, "data": [ /* BloodPressureResponse[] */ ] }
```

---

### `GET /patients/{patient_id}/blood-pressure/stats` ✨ convertido de mock

Estatísticas agregadas sobre dados reais.

**Tela mobile:** card de resumo em `PressaoScreen`

**Resposta 200:**
```json
{
  "patient_id": "<uuid>",
  "total_readings": 20,
  "average_systolic": 118.5,
  "average_diastolic": 78.2,
  "last_reading": {
    "systolic": 120,
    "diastolic": 80,
    "classification": "normal",
    "timestamp": "2024-03-15T07:30:00"
  }
}
```

---

### `GET /patients/{patient_id}/blood-pressure/chart` ✨ convertido de mock

Série temporal dupla (sistólica + diastólica) para gráfico de linhas.

**Tela mobile:** gráfico em `PressaoScreen`

**Query params:** `days` (padrão 30, máx 365)

**Resposta 200:**
```json
{
  "data": [
    { "timestamp": "2024-02-14T07:30:00", "systolic": 118, "diastolic": 78 }
  ],
  "hypertension_limit": 140,
  "normal_systolic": 120,
  "normal_diastolic": 80
}
```

---

## Grupo 7 — Exames

### `POST /patients/{patient_id}/ultrasounds`

Registra laudo de ultrassonografia. Requer role `doctor` ou `admin`.

**Tela mobile:** formulário de registro de USG (médico)

**Body:** campos do `UltrasoundCreate` (data, semana gestacional, biometrias, observações)

**Resposta 201:** objeto `UltrasoundResponse`

---

### `GET /patients/{patient_id}/ultrasounds` ✨ convertido de mock

Lista histórico paginado de ultrassonografias reais do banco.

**Tela mobile:** `UltrassomScreen` — lista de laudos

**Query params:** `limit` (padrão 20), `offset`

**Resposta 200:**
```json
{ "total": 3, "limit": 20, "offset": 0, "data": [ /* UltrasoundResponse[] */ ] }
```

---

### `POST /patients/{patient_id}/vaccines` ✨ novo

Registra vacina ou agendamento. Requer role `doctor` ou `admin`.

**Tela mobile:** formulário de vacinação (médico)

**Body:**
```json
{
  "vaccine_type": "Hepatite B",
  "date": "2024-03-01",
  "dose_number": 1,
  "status": "applied",
  "reactions": null
}
```

Valores válidos para `status`: `scheduled`, `applied`, `missed`

**Resposta 201:** objeto `VaccineResponse`

---

### `GET /patients/{patient_id}/vaccines` ✨ novo

Lista cartão de vacinação da paciente.

**Tela mobile:** `VacinasScreen`

**Query params:** `limit` (padrão 50), `offset`

**Resposta 200:**
```json
{ "total": 8, "limit": 50, "offset": 0, "data": [ /* VaccineResponse[] */ ] }
```

---

### `PATCH /patients/vaccines/{vaccine_id}` ✨ novo

Atualiza status ou reações adversas de uma vacina. Requer role `doctor` ou `admin`.

**Body (todos opcionais):**
```json
{ "status": "applied", "reactions": "Dor local leve" }
```

**Resposta 200:** objeto `VaccineResponse` atualizado

**Erros:**
- `404` — vacina não encontrada

---

## Grupo 8 — Avisos da Clínica

### `GET /clinics/{clinic_id}/announcements` ✨ novo

Lista avisos não expirados da clínica, com campo `is_new` (`true` se criado nos últimos 7 dias).

**Tela mobile:** `AvisosScreen` — elimina os 5 avisos hardcoded

**Query params:**
- `category` (opcional): `agenda`, `saude`, `clinica`, `geral`
- `limit` (padrão 20), `offset`

**Resposta 200:**
```json
{
  "total": 5,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "clinic_id": "<uuid>",
      "category": "saude",
      "title": "Vacinação disponível",
      "short_description": "Vacina da gripe disponível na clínica.",
      "full_description": "...",
      "expires_at": "2024-04-30T00:00:00",
      "is_new": true,
      "created_at": "2024-03-20T10:00:00"
    }
  ]
}
```

---

### `POST /clinics/{clinic_id}/announcements` ✨ novo

Publica novo aviso. Requer role `secretary` ou `admin`.

**Tela mobile:** painel da secretária — criar aviso

**Body:**
```json
{
  "category": "agenda",
  "title": "Mudança de horário",
  "short_description": "Consultas de sexta serão das 8h às 12h.",
  "full_description": "A partir do dia 01/04, os atendimentos de sexta-feira...",
  "expires_at": "2024-04-30T23:59:59"
}
```

`expires_at` é opcional. Se omitido, o aviso não expira.

**Resposta 201:** objeto `AnnouncementResponse`

---

## Grupo 9 — Dashboard e Agenda do Médico

### `GET /doctors/{doctor_id}/patients` ✨ novo

Lista pacientes do médico com filtros e paginação. Requer role `doctor` ou `admin`.

**Tela mobile:** `PacientesScreen` (médico) — lista com busca e filtro de risco

**Query params:**
- `search` (opcional): busca por nome ou número de prontuário
- `risk_level` (opcional): `low`, `medium`, `high`
- `limit` (padrão 20, máx 100), `offset`

**Resposta 200:**
```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "user_id": "<uuid>",
      "prontuario": "PR-98765",
      "current_week": 24,
      "edd": "2024-08-07",
      "risk_level": "low",
      "user": { "name": "Maria da Silva", "phone": "(11) 99999-9999" }
    }
  ]
}
```

---

### `GET /doctors/{doctor_id}/dashboard` ✨ novo

Estatísticas do dia para o médico. Requer role `doctor` ou `admin`.

**Tela mobile:** `DashboardScreen` (médico) — cards "Consultas hoje" e "Pacientes ativas"

**Resposta 200:**
```json
{
  "appointments_today": 8,
  "active_patients": 42
}
```

---

### `GET /doctors/{doctor_id}/agenda` ✨ novo

Agenda do médico em três visualizações. Requer role `doctor` ou `admin`.

**Tela mobile:** `AgendaScreen` — abas dia / semana / partos

**Query params:**
- `view`: `day` | `week` | `births` (obrigatório)
- `date`: data de referência no formato `YYYY-MM-DD` (padrão: hoje)

**Resposta — view=day:**
```json
{
  "view": "day",
  "date": "2024-03-15",
  "appointments": [
    {
      "id": "<uuid>",
      "date": "2024-03-15",
      "time": "09:00:00",
      "duration_minutes": 30,
      "type": "consulta",
      "status": "confirmed",
      "patient_status": "waiting",
      "location": "Consultório 1",
      "notes": null
    }
  ]
}
```

**Resposta — view=week:**
```json
{
  "view": "week",
  "start": "2024-03-11",
  "appointments": [
    { "id": "<uuid>", "date": "2024-03-12", "time": "10:00:00", "duration_minutes": 30, "type": "retorno", "status": "pending" }
  ]
}
```

**Resposta — view=births:**
Partos previstos nos próximos 60 dias, ordenados por DPP.
```json
{
  "view": "births",
  "upcoming_births": [
    {
      "patient_id": "<uuid>",
      "name": "Maria da Silva",
      "edd": "2024-04-02",
      "current_week": 38,
      "risk_level": "low",
      "hospital": "Maternidade Santa Joana"
    }
  ]
}
```

---

## Grupo 10 — Dashboard e Cadastro (Secretária)

### `GET /secretary/dashboard` ✨ novo

Estatísticas do dia para a clínica inteira. Requer role `secretary` ou `admin`. O `clinic_id` é extraído do token da secretária autenticada.

**Tela mobile:** `DashboardScreen` (secretária) — cards de totais diários

**Resposta 200:**
```json
{
  "appointments_today": 15,
  "confirmed": 10,
  "pending": 5,
  "total_patients": 120
}
```

---

### `POST /patients` ✨ novo

Cadastra nova paciente criando `User` (role=patient) e `Patient` em uma única transação. Requer role `secretary` ou `admin`.

**Tela mobile:** `CadastrarPacienteScreen` (secretária)

**Query params (obrigatórios):**
- `doctor_id`: UUID do médico responsável
- `prontuario`: número do prontuário
- `lmp_date`: data da última menstruação (`YYYY-MM-DD`)
- `edd`: data provável do parto (`YYYY-MM-DD`)

**Body:**
```json
{
  "name": "Ana Costa",
  "email": "ana@email.com",
  "phone": "(11) 98765-4321",
  "password": "senha_temporaria_123",
  "role": "patient",
  "clinic_id": "<uuid>"
}
```

**Resposta 201:** objeto `UserResponse` do usuário criado

---

## Migrations

Aplicar todas de uma vez:

```bash
alembic upgrade head
```

| Migration ID | O que cria |
|---|---|
| `a1b2c3d4e5f6` | `announcements` |
| `b1c2d3e4f5a6` | `lab_tests`, `medications`, col `push_token` e `onboarding_completed` em `users` |
| `c1d2e3f4a5b6` | `notifications`, `reminders` |
| `d1e2f3a4b5c6` | `baby_names`, `patient_baby_name_favorites`, `fetal_development` |
| `e1f2a3b4c5d6` | `messages`, `user_announcement_reads` |

Após migrar, popular dados estáticos (uma única vez):

```bash
python alembic/seeds/baby_names.py        # 203 nomes
python alembic/seeds/fetal_development.py # semanas 1–42
```

---

## Resumo por Role

| Role | Acesso (v1 + v2) |
|---|---|
| `patient` | Próprios vitais, prontuário, ultrassons, vacinas, avisos da clínica, exames laboratoriais, medicamentos, notificações, chat, nomes de bebê (favoritos), desenvolvimento fetal |
| `doctor` | Tudo do patient + registrar USG/vacina/exame/medicamento + dashboard + agenda + lista de pacientes + agendamento por paciente |
| `secretary` | Dashboard + relatório diário + cadastrar pacientes + publicar avisos + enviar lembretes |
| `admin` | Acesso total (equivalente a doctor + secretary) |

> Todos os endpoints de v2 estão documentados em **`API_V2_BACKLOG.md`**.
> Não há mais endpoints retornando dados mock — todos foram implementados com dados reais.
