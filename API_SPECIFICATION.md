# Especificação de API RESTful — Lunna

**Aplicativo de Acompanhamento Pré-natal para Gestantes em Clínicas Privadas**

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Recursos e Endpoints](#recursos-e-endpoints)
4. [Estruturas de Dados](#estruturas-de-dados)
5. [Padrões RESTful](#padrões-restful)
6. [Fluxos Principais](#fluxos-principais)
7. [Considerações de Segurança](#considerações-de-segurança)
8. [Observações Técnicas](#observações-técnicas)

---

## Visão Geral

### Contexto do Projeto

**Lunna** é um aplicativo mobile-first de acompanhamento pré-natal voltado para gestantes em atendimento privado em clínicas. O app suporta 3 perfis distintos:

- **Paciente (Gestante):** Monitora gravidez, registra sinais vitais, consulta dados clínicos
- **Médico(a):** Acompanha pacientes, edita prontuários, acessa dados clínicos detalhados
- **Secretária:** Gerencia agenda, cadastra pacientes, envia lembretes

### Modelo de Negócio

**SaaS White-label**: vender o app para várias clínicas, cada uma personalizando logo e cores.

### Tech Stack da API

- **Framework:** Node.js/Express ou Next.js (backend)
- **Banco de Dados:** Supabase (PostgreSQL)
- **Autenticação:** JWT (Bearer Token)
- **Versionamento de API:** `/api/v1/`

---

## Autenticação

### Fluxo de Autenticação

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@clinic.com",
  "password": "senha_segura"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "usr_123",
    "email": "usuario@clinic.com",
    "name": "Maria da Silva",
    "role": "patient", // patient, doctor, secretary
    "clinic_id": "clinic_456",
    "avatar_url": "https://..."
  }
}
```

### Fluxo de Refresh Token

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Headers Padrão

Todas as requisições protegidas devem incluir:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Roles e Permissões

| Role | Permissões Principais |
|------|----------------------|
| **patient** | Ler próprios dados, registrar sinais vitais, confirmar consultas, chat |
| **doctor** | Ler/editar dados de pacientes, criar/atualizar registros clínicos, agenda |
| **secretary** | Criar agendamentos, cadastrar pacientes, enviar lembretes, relatórios |
| **admin** | Gerenciar clínica, usuários, configurações |
| **superadmin** | Controle global: cadastrar/gerenciar clínicas e administradores globais |

---

## Recursos e Endpoints

### 1. USUÁRIOS & AUTENTICAÇÃO

#### POST `/api/v1/auth/login`
Autenticar usuário com email e senha.

**Request:**
```json
{
  "email": "maria@clinic.com",
  "password": "senha123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "user": {
    "id": "usr_123",
    "email": "maria@clinic.com",
    "name": "Maria da Silva",
    "role": "patient",
    "clinic_id": "clinic_456",
    "avatar_url": "https://..."
  }
}
```

#### POST `/api/v1/auth/register`
Criar novo usuário.

**Request:**
```json
{
  "email": "novo@clinic.com",
  "password": "senha123",
  "name": "João Silva",
  "role": "patient", // patient, doctor, secretary
  "clinic_id": "clinic_456",
  "phone": "(11) 99999-9999"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_124",
  "email": "novo@clinic.com",
  "name": "João Silva",
  "role": "patient",
  "clinic_id": "clinic_456"
}
```

#### POST `/api/v1/auth/logout`
Finalizar sessão.

**Response (200 OK):**
```json
{ "message": "Logged out successfully" }
```

#### GET `/api/v1/users/:user_id`
Obter dados do perfil do usuário.

**Response (200 OK):**
```json
{
  "id": "usr_123",
  "email": "maria@clinic.com",
  "name": "Maria da Silva",
  "role": "patient",
  "clinic_id": "clinic_456",
  "avatar_url": "https://...",
  "phone": "(11) 99999-9999",
  "date_of_birth": "1990-05-15",
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z"
}
```

#### PUT `/api/v1/users/:user_id`
Atualizar dados do perfil.

**Request:**
```json
{
  "name": "Maria Silva Santos",
  "avatar_url": "https://new-avatar.jpg",
  "phone": "(11) 98888-8888"
}
```

**Response (200 OK):**
```json
{
  "id": "usr_123",
  "name": "Maria Silva Santos",
  "avatar_url": "https://new-avatar.jpg",
  "phone": "(11) 98888-8888",
  "updated_at": "2024-01-11T15:30:00Z"
}
```

#### GET `/api/v1/users/:user_id/clinic`
Obter informações da clínica do usuário.

**Response (200 OK):**
```json
{
  "id": "clinic_456",
  "name": "Clínica Lunna",
  "logo_url": "https://...",
  "primary_color": "#8DAA91",
  "secondary_color": "#E5987D",
  "address": "Rua X, 123, São Paulo, SP",
  "phone": "(11) 3000-0000",
  "website": "https://lunnaclinica.com.br"
}
```

#### PATCH `/api/v1/users/:user_id/preferences`
Atualizar preferências do usuário (notificações, tema, etc.).

**Request:**
```json
{
  "notifications_enabled": true,
  "email_notifications": true,
  "push_notifications": true,
  "language": "pt-BR",
  "theme": "light"
}
```

**Response (200 OK):**
```json
{
  "id": "usr_123",
  "preferences": {
    "notifications_enabled": true,
    "email_notifications": true,
    "push_notifications": true,
    "language": "pt-BR",
    "theme": "light"
  },
  "updated_at": "2024-01-11T16:00:00Z"
}
```

---

### 2. CONSULTAS/AGENDAMENTOS

#### GET `/api/v1/patients/:patient_id/appointments`
Listar todas as consultas da paciente.

**Query Parameters:**
- `status`: pending, confirmed, completed, cancelled
- `limit`: número de registros (padrão: 20)
- `offset`: paginação (padrão: 0)

**Response (200 OK):**
```json
{
  "total": 5,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "apt_001",
      "patient_id": "usr_123",
      "doctor_id": "usr_456",
      "doctor_name": "Dra. Ana Lima",
      "clinic_id": "clinic_456",
      "date": "2024-02-15",
      "time": "14:30",
      "datetime": "2024-02-15T14:30:00Z",
      "status": "confirmed", // pending, confirmed, completed, cancelled
      "type": "routine", // routine, ultrasound, lab
      "location": "Sala 302 - Clínica Lunna",
      "notes": "Acompanhamento de rotina",
      "patient_status": "confirmed", // confirmed, pending, reschedule_requested, reschedule_approved
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

#### GET `/api/v1/appointments/:appointment_id`
Obter detalhes de uma consulta específica.

**Response (200 OK):**
```json
{
  "id": "apt_001",
  "patient_id": "usr_123",
  "doctor_id": "usr_456",
  "doctor_name": "Dra. Ana Lima",
  "doctor_avatar": "https://...",
  "clinic_id": "clinic_456",
  "clinic_name": "Clínica Lunna",
  "date": "2024-02-15",
  "time": "14:30",
  "datetime": "2024-02-15T14:30:00Z",
  "status": "confirmed",
  "type": "routine",
  "duration_minutes": 30,
  "location": "Sala 302",
  "address": "Rua X, 123, São Paulo, SP",
  "phone": "(11) 3000-0000",
  "notes": "Acompanhamento de rotina",
  "patient_status": "confirmed",
  "confirmed_at": "2024-02-01T10:15:00Z",
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z"
}
```

#### POST `/api/v1/doctors/:doctor_id/appointments`
Criar novo agendamento (feito pela secretária ou sistema de disponibilidade).

**Request:**
```json
{
  "patient_id": "usr_123",
  "date": "2024-02-15",
  "time": "14:30",
  "type": "routine",
  "notes": "Acompanhamento de rotina"
}
```

**Response (201 Created):**
```json
{
  "id": "apt_001",
  "patient_id": "usr_123",
  "doctor_id": "usr_456",
  "date": "2024-02-15",
  "time": "14:30",
  "status": "pending",
  "patient_status": "pending",
  "created_at": "2024-01-10T10:00:00Z"
}
```

#### PATCH `/api/v1/appointments/:appointment_id/confirm`
Confirmar presença na consulta (paciente confirma).

**Request:**
```json
{
  "confirmed": true
}
```

**Response (200 OK):**
```json
{
  "id": "apt_001",
  "patient_status": "confirmed",
  "confirmed_at": "2024-02-01T10:15:00Z",
  "updated_at": "2024-02-01T10:15:00Z"
}
```

#### POST `/api/v1/appointments/:appointment_id/reschedule-request`
Solicitar remarcação de consulta.

**Request:**
```json
{
  "reason": "conflito_pessoal", // conflito_pessoal, problema_saude, outro
  "observation": "Não posso ir no horário"
}
```

**Response (201 Created):**
```json
{
  "id": "apt_001",
  "patient_status": "reschedule_requested",
  "reschedule_reason": "conflito_pessoal",
  "reschedule_observation": "Não posso ir no horário",
  "reschedule_requested_at": "2024-02-01T10:15:00Z",
  "updated_at": "2024-02-01T10:15:00Z"
}
```

#### PATCH `/api/v1/appointments/:appointment_id/reschedule/approve`
Médica aprova remarcação e define nova data.

**Request:**
```json
{
  "new_date": "2024-02-22",
  "new_time": "15:00"
}
```

**Response (200 OK):**
```json
{
  "id": "apt_001",
  "date": "2024-02-22",
  "time": "15:00",
  "patient_status": "reschedule_approved",
  "reschedule_approved_at": "2024-02-02T09:30:00Z",
  "updated_at": "2024-02-02T09:30:00Z"
}
```

#### DELETE `/api/v1/appointments/:appointment_id`
Cancelar consulta.

**Request:**
```json
{
  "reason": "paciente_desistiu" // paciente_desistiu, medica_cancelou, outro
}
```

**Response (204 No Content)**

#### GET `/api/v1/doctors/:doctor_id/schedule`
Obter agenda da médica (filtrável por período).

**Query Parameters:**
- `view`: day, week, month (padrão: month)
- `date`: YYYY-MM-DD (data de referência)

**Response (200 OK):**
```json
{
  "doctor_id": "usr_456",
  "doctor_name": "Dra. Ana Lima",
  "clinic_id": "clinic_456",
  "view": "month",
  "date": "2024-02-15",
  "data": [
    {
      "date": "2024-02-15",
      "appointments": [
        {
          "id": "apt_001",
          "time": "10:00",
          "patient_name": "Maria da Silva",
          "status": "confirmed",
          "type": "routine"
        },
        {
          "id": "apt_002",
          "time": "14:30",
          "patient_name": "João da Silva",
          "status": "pending",
          "type": "ultrasound"
        }
      ]
    }
  ]
}
```

#### GET `/api/v1/patients/:patient_id/appointments/next`
Obter próxima consulta agendada.

**Response (200 OK):**
```json
{
  "id": "apt_001",
  "patient_id": "usr_123",
  "doctor_name": "Dra. Ana Lima",
  "date": "2024-02-15",
  "time": "14:30",
  "days_until": 4,
  "location": "Sala 302",
  "status": "confirmed"
}
```

---

### 3. SINAIS VITAIS

#### CONTRAÇÕES

##### POST `/api/v1/patients/:patient_id/contractions`
Registrar nova contração.

**Request:**
```json
{
  "duration_seconds": 45,
  "timestamp": "2024-02-15T10:30:00Z",
  "interval_minutes": 5
}
```

**Response (201 Created):**
```json
{
  "id": "ctr_001",
  "patient_id": "usr_123",
  "duration_seconds": 45,
  "timestamp": "2024-02-15T10:30:00Z",
  "interval_minutes": 5,
  "created_at": "2024-02-15T10:30:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/contractions`
Listar contrações registradas.

**Query Parameters:**
- `date`: YYYY-MM-DD (filtrar por data)
- `limit`: número de registros
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 12,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "ctr_001",
      "duration_seconds": 45,
      "timestamp": "2024-02-15T10:30:00Z",
      "interval_minutes": 5,
      "index": 1
    },
    {
      "id": "ctr_002",
      "duration_seconds": 50,
      "timestamp": "2024-02-15T10:35:00Z",
      "interval_minutes": 5,
      "index": 2
    }
  ]
}
```

##### GET `/api/v1/patients/:patient_id/contractions/stats`
Obter estatísticas de contrações.

**Response (200 OK):**
```json
{
  "patient_id": "usr_123",
  "total_contractions": 12,
  "average_duration_seconds": 47,
  "average_interval_minutes": 5.2,
  "last_contraction": "2024-02-15T10:45:00Z",
  "date": "2024-02-15"
}
```

##### DELETE `/api/v1/patients/:patient_id/contractions/session`
Limpar sessão de contrações do dia.

**Response (204 No Content)**

---

#### GLICOSE

##### POST `/api/v1/patients/:patient_id/glucose-readings`
Registrar leitura de glicose.

**Request:**
```json
{
  "value_mg_dl": 95,
  "moment": "fasting", // fasting, after_meal, random
  "notes": "Após café da manhã",
  "timestamp": "2024-02-15T08:30:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "glc_001",
  "patient_id": "usr_123",
  "value_mg_dl": 95,
  "moment": "fasting",
  "notes": "Após café da manhã",
  "classification": "Normal", // Normal, Atenção, Alto
  "timestamp": "2024-02-15T08:30:00Z",
  "created_at": "2024-02-15T08:30:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/glucose-readings`
Listar histórico de glicose.

**Query Parameters:**
- `days`: 7, 30, 90 (padrão: 30)
- `limit`: número de registros
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 15,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "glc_001",
      "value_mg_dl": 95,
      "moment": "fasting",
      "notes": "Após café da manhã",
      "classification": "Normal",
      "timestamp": "2024-02-15T08:30:00Z",
      "created_at": "2024-02-15T08:30:00Z"
    }
  ]
}
```

##### GET `/api/v1/patients/:patient_id/glucose-readings/stats`
Obter estatísticas de glicose.

**Response (200 OK):**
```json
{
  "patient_id": "usr_123",
  "total_readings": 15,
  "last_reading": 95,
  "average": 92,
  "min": 78,
  "max": 110,
  "status": "Normal", // Normal, Atenção, Alto
  "days_tracked": 30
}
```

##### GET `/api/v1/patients/:patient_id/glucose-readings/chart`
Obter dados para gráfico (Canvas).

**Query Parameters:**
- `days`: 7, 30, 90 (padrão: 30)

**Response (200 OK):**
```json
{
  "data": [
    {
      "timestamp": "2024-02-01T08:00:00Z",
      "value": 90,
      "moment": "fasting"
    },
    {
      "timestamp": "2024-02-02T08:00:00Z",
      "value": 95,
      "moment": "fasting"
    }
  ],
  "normal_limit": 95,
  "hypertension_limit": 126
}
```

---

#### PRESSÃO ARTERIAL

##### POST `/api/v1/patients/:patient_id/blood-pressure`
Registrar leitura de pressão arterial.

**Request:**
```json
{
  "systolic": 120,
  "diastolic": 80,
  "pulse_bpm": 72,
  "moment": "morning", // morning, afternoon, evening, night
  "timestamp": "2024-02-15T08:30:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "bp_001",
  "patient_id": "usr_123",
  "systolic": 120,
  "diastolic": 80,
  "pulse_bpm": 72,
  "moment": "morning",
  "classification": "Normal", // Normal, Atenção, Alto
  "timestamp": "2024-02-15T08:30:00Z",
  "created_at": "2024-02-15T08:30:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/blood-pressure`
Listar histórico de pressão arterial.

**Query Parameters:**
- `days`: 7, 30, 90 (padrão: 30)
- `limit`: número de registros
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 10,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "bp_001",
      "systolic": 120,
      "diastolic": 80,
      "pulse_bpm": 72,
      "moment": "morning",
      "classification": "Normal",
      "timestamp": "2024-02-15T08:30:00Z"
    }
  ]
}
```

##### GET `/api/v1/patients/:patient_id/blood-pressure/stats`
Obter estatísticas de pressão arterial.

**Response (200 OK):**
```json
{
  "patient_id": "usr_123",
  "total_readings": 10,
  "average_systolic": 118,
  "average_diastolic": 78,
  "max_systolic": 130,
  "max_diastolic": 85,
  "status": "Normal", // Normal, Atenção, Alto
  "hypertension_risk": false
}
```

##### GET `/api/v1/patients/:patient_id/blood-pressure/chart`
Obter dados para gráfico duplo (systolic/diastolic).

**Query Parameters:**
- `days`: 7, 30, 90 (padrão: 30)

**Response (200 OK):**
```json
{
  "data": [
    {
      "timestamp": "2024-02-01T08:00:00Z",
      "systolic": 118,
      "diastolic": 76
    },
    {
      "timestamp": "2024-02-02T08:00:00Z",
      "systolic": 120,
      "diastolic": 80
    }
  ],
  "hypertension_limit": 140,
  "normal_systolic": 120,
  "normal_diastolic": 80
}
```

---

### 4. EXAMES & DADOS CLÍNICOS

#### ULTRASSOM (USG)

##### POST `/api/v1/patients/:patient_id/ultrasounds`
Registrar ultrassom.

**Request:**
```json
{
  "type": "obstetric", // obstetric, morphology, detailed
  "date": "2024-02-15",
  "ig_weeks": 24,
  "presentation": "cephalic", // cephalic, breech, transverse
  "placenta_location": "anterior",
  "amniotic_fluid_ml": 850,
  "fetal_heart_rate": 150,
  "fetal_weight_g": 620,
  "percentile": 50,
  "notes": "Normal development"
}
```

**Response (201 Created):**
```json
{
  "id": "usg_001",
  "patient_id": "usr_123",
  "type": "obstetric",
  "date": "2024-02-15",
  "ig_weeks": 24,
  "presentation": "cephalic",
  "placenta_location": "anterior",
  "amniotic_fluid_ml": 850,
  "fetal_heart_rate": 150,
  "fetal_weight_g": 620,
  "percentile": 50,
  "notes": "Normal development",
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/ultrasounds`
Listar ultrassons.

**Response (200 OK):**
```json
{
  "total": 3,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "usg_001",
      "type": "obstetric",
      "date": "2024-02-15",
      "ig_weeks": 24,
      "fetal_heart_rate": 150,
      "created_at": "2024-02-15T10:00:00Z"
    }
  ]
}
```

##### GET `/api/v1/ultrasounds/:usg_id`
Obter detalhes de um ultrassom.

**Response (200 OK):**
```json
{
  "id": "usg_001",
  "patient_id": "usr_123",
  "type": "obstetric",
  "date": "2024-02-15",
  "ig_weeks": 24,
  "presentation": "cephalic",
  "placenta_location": "anterior",
  "amniotic_fluid_ml": 850,
  "fetal_heart_rate": 150,
  "fetal_weight_g": 620,
  "percentile": 50,
  "notes": "Normal development",
  "image_url": "https://...",
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### PUT `/api/v1/ultrasounds/:usg_id`
Atualizar ultrassom.

**Request:**
```json
{
  "presentation": "cephalic",
  "notes": "Updated notes"
}
```

**Response (200 OK):**
```json
{
  "id": "usg_001",
  "presentation": "cephalic",
  "notes": "Updated notes",
  "updated_at": "2024-02-15T11:00:00Z"
}
```

---

#### EXAMES LABORATORIAIS

##### POST `/api/v1/patients/:patient_id/lab-tests`
Registrar coleta laboratorial.

**Request:**
```json
{
  "date": "2024-02-15",
  "hemoglobin": 12.5,
  "hematocrit": 37,
  "platelets": 250,
  "fasting_glucose": 95,
  "tsh": 2.1,
  "ferritin": 45,
  "vitamin_d": 28,
  "b12": 450,
  "eas": "normal",
  "urine_culture": "negative",
  "serology": {
    "hiv": "negative",
    "syphilis": "negative",
    "hepatitis_b": "negative",
    "hepatitis_c": "negative",
    "rubella": "immune",
    "toxoplasmosis": "negative",
    "cmv": "negative",
    "herpes": "negative",
    "group_b_strep": "negative"
  },
  "notes": "All normal"
}
```

**Response (201 Created):**
```json
{
  "id": "lab_001",
  "patient_id": "usr_123",
  "date": "2024-02-15",
  "hemoglobin": 12.5,
  "hematocrit": 37,
  "platelets": 250,
  "fasting_glucose": 95,
  "tsh": 2.1,
  "ferritin": 45,
  "vitamin_d": 28,
  "b12": 450,
  "eas": "normal",
  "urine_culture": "negative",
  "serology": { /* ... */ },
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/lab-tests`
Listar exames laboratoriais.

**Response (200 OK):**
```json
{
  "total": 2,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "lab_001",
      "date": "2024-02-15",
      "hemoglobin": 12.5,
      "hematocrit": 37,
      "created_at": "2024-02-15T10:00:00Z"
    }
  ]
}
```

##### GET `/api/v1/lab-tests/:test_id`
Obter detalhes de um exame.

##### PUT `/api/v1/lab-tests/:test_id`
Atualizar exame laboratorial.

---

#### VACINAS

##### POST `/api/v1/patients/:patient_id/vaccines`
Registrar dose de vacina.

**Request:**
```json
{
  "vaccine_type": "tetanus", // tetanus, influenza, covid19, etc
  "date": "2024-02-15",
  "dose_number": 1,
  "status": "completed", // scheduled, completed, missed
  "reactions": "arm pain at injection site"
}
```

**Response (201 Created):**
```json
{
  "id": "vac_001",
  "patient_id": "usr_123",
  "vaccine_type": "tetanus",
  "date": "2024-02-15",
  "dose_number": 1,
  "status": "completed",
  "reactions": "arm pain at injection site",
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/vaccines`
Listar vacinas.

**Response (200 OK):**
```json
{
  "total": 4,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "vac_001",
      "vaccine_type": "tetanus",
      "date": "2024-02-15",
      "dose_number": 1,
      "status": "completed",
      "created_at": "2024-02-15T10:00:00Z"
    }
  ]
}
```

##### PATCH `/api/v1/vaccines/:vaccine_id`
Atualizar status de vacina.

**Request:**
```json
{
  "status": "completed",
  "reactions": "leve dor no braço"
}
```

**Response (200 OK):**
```json
{
  "id": "vac_001",
  "status": "completed",
  "reactions": "leve dor no braço",
  "updated_at": "2024-02-15T11:00:00Z"
}
```

---

#### PESO & ALTURA UTERINA

##### POST `/api/v1/patients/:patient_id/weight`
Registrar peso gestacional.

**Request:**
```json
{
  "weight_kg": 75.5,
  "week_number": 24,
  "timestamp": "2024-02-15T10:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "wgt_001",
  "patient_id": "usr_123",
  "weight_kg": 75.5,
  "week_number": 24,
  "timestamp": "2024-02-15T10:00:00Z",
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/weight`
Listar evolução do peso.

**Response (200 OK):**
```json
{
  "total": 6,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "wgt_001",
      "weight_kg": 75.5,
      "week_number": 24,
      "timestamp": "2024-02-15T10:00:00Z"
    }
  ]
}
```

##### POST `/api/v1/patients/:patient_id/uterine-height`
Registrar altura uterina.

**Request:**
```json
{
  "height_cm": 24,
  "week_number": 24,
  "timestamp": "2024-02-15T10:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "uh_001",
  "patient_id": "usr_123",
  "height_cm": 24,
  "week_number": 24,
  "timestamp": "2024-02-15T10:00:00Z",
  "created_at": "2024-02-15T10:00:00Z"
}
```

##### GET `/api/v1/patients/:patient_id/uterine-height`
Listar altura uterina.

---

### 5. PRONTUÁRIO/CARTÃO CLÍNICO

#### GET `/api/v1/patients/:patient_id/medical-record`
Obter cartão clínico completo.

**Response (200 OK):**
```json
{
  "id": "mr_001",
  "patient_id": "usr_123",
  "identification": {
    "baby_name": "João",
    "companion": "Pedro Silva",
    "hospital": "Hospital X",
    "risk_classification": "low", // low, medium, high
    "height_cm": 165,
    "weight_initial_kg": 65,
    "imc": 23.9,
    "number_of_fetuses": 1,
    "parity": "G2P1", // gravidity/parity
    "risk_factors": ["gestational_diabetes"],
    "edd": "2024-06-15", // estimated due date
    "cesarean_predicted": false
  },
  "clinical_data": {
    "allergies": ["penicillin"],
    "medications": ["prenatal_vitamin"],
    "chronic_diseases": ["hypertension"],
    "previous_surgeries": ["appendectomy"],
    "gynecological_history": "normal",
    "family_history": "diabetes",
    "occupation": "teacher",
    "habits": "non-smoker",
    "observations": ""
  },
  "special_exams": {
    "blood_type": "O+",
    "nipt": "negative",
    "glucose_curve": {
      "fasting": 90,
      "one_hour": 140,
      "two_hours": 130,
      "status": "Normal"
    },
    "group_b_strep": "negative" // negative, positive, pending
  },
  "doctor_notes": {
    "content": "Patient is doing well...",
    "updated_at": "2024-02-15T10:00:00Z"
  },
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-02-15T10:00:00Z"
}
```

#### PATCH `/api/v1/patients/:patient_id/medical-record/identification`
Atualizar identificação.

**Request:**
```json
{
  "baby_name": "João",
  "companion": "Pedro Silva",
  "hospital": "Hospital X",
  "risk_classification": "low",
  "height_cm": 165,
  "weight_initial_kg": 65,
  "number_of_fetuses": 1,
  "parity": "G2P1",
  "risk_factors": ["gestational_diabetes"],
  "cesarean_predicted": false
}
```

**Response (200 OK):**
```json
{
  "identification": { /* ... */ },
  "updated_at": "2024-02-15T10:00:00Z"
}
```

#### PATCH `/api/v1/patients/:patient_id/medical-record/clinical-data`
Atualizar dados clínicos.

**Request:**
```json
{
  "allergies": ["penicillin"],
  "medications": ["prenatal_vitamin"],
  "chronic_diseases": ["hypertension"],
  "previous_surgeries": ["appendectomy"],
  "gynecological_history": "normal",
  "family_history": "diabetes",
  "occupation": "teacher",
  "habits": "non-smoker",
  "observations": ""
}
```

**Response (200 OK):**
```json
{
  "clinical_data": { /* ... */ },
  "updated_at": "2024-02-15T10:00:00Z"
}
```

#### PATCH `/api/v1/patients/:patient_id/medical-record/special-exams`
Atualizar exames especiais.

**Request:**
```json
{
  "blood_type": "O+",
  "nipt": "negative",
  "glucose_curve": {
    "fasting": 90,
    "one_hour": 140,
    "two_hours": 130,
    "status": "Normal"
  },
  "group_b_strep": "negative"
}
```

**Response (200 OK):**
```json
{
  "special_exams": { /* ... */ },
  "updated_at": "2024-02-15T10:00:00Z"
}
```

#### GET `/api/v1/patients/:patient_id/medical-record/doctor-notes`
Obter notas privadas da médica.

**Response (200 OK):**
```json
{
  "content": "Patient is doing well...",
  "updated_at": "2024-02-15T10:00:00Z",
  "updated_by": "usr_456"
}
```

#### PATCH `/api/v1/patients/:patient_id/medical-record/doctor-notes`
Atualizar notas (auto-save com debounce 800ms).

**Request:**
```json
{
  "content": "Patient is doing well. Continue monitoring."
}
```

**Response (200 OK):**
```json
{
  "content": "Patient is doing well. Continue monitoring.",
  "updated_at": "2024-02-15T10:00:00Z",
  "updated_by": "usr_456"
}
```

#### GET `/api/v1/patients/:patient_id/risk-level`
Obter classificação de risco.

**Response (200 OK):**
```json
{
  "patient_id": "usr_123",
  "risk_level": "low", // low, medium, high
  "factors": ["gestational_diabetes"],
  "classification_date": "2024-02-15",
  "reviewed_by": "usr_456"
}
```

#### PATCH `/api/v1/patients/:patient_id/risk-level`
Atualizar classificação de risco.

**Request:**
```json
{
  "risk_level": "medium",
  "reason": "gestational_diabetes_detected"
}
```

**Response (200 OK):**
```json
{
  "risk_level": "medium",
  "reason": "gestational_diabetes_detected",
  "updated_at": "2024-02-15T10:00:00Z"
}
```

---

### 6. CHAT/MENSAGENS

#### POST `/api/v1/patients/:patient_id/messages`
Enviar mensagem.

**Request:**
```json
{
  "message_text": "Oi Dra. Ana, como vai?",
  "timestamp": "2024-02-15T10:30:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "msg_001",
  "patient_id": "usr_123",
  "sender_type": "patient",
  "message_text": "Oi Dra. Ana, como vai?",
  "timestamp": "2024-02-15T10:30:00Z",
  "read": false,
  "created_at": "2024-02-15T10:30:00Z"
}
```

#### GET `/api/v1/patients/:patient_id/messages`
Obter histórico do chat.

**Query Parameters:**
- `limit`: número de mensagens (padrão: 50)
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 25,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "msg_001",
      "sender_type": "patient",
      "sender_name": "Maria da Silva",
      "sender_avatar": "https://...",
      "message_text": "Oi Dra. Ana, como vai?",
      "timestamp": "2024-02-15T10:30:00Z",
      "read": true,
      "read_at": "2024-02-15T10:35:00Z"
    },
    {
      "id": "msg_002",
      "sender_type": "doctor",
      "sender_name": "Dra. Ana Lima",
      "sender_avatar": "https://...",
      "message_text": "Oi Maria! Tudo bem? Como você está se sentindo?",
      "timestamp": "2024-02-15T10:36:00Z",
      "read": true,
      "read_at": "2024-02-15T10:40:00Z"
    }
  ]
}
```

#### GET `/api/v1/messages/quick-replies`
Obter sugestões de resposta rápida.

**Query Parameters:**
- `context`: pregnancy_monitoring, appointment, vital_sign (opcional)

**Response (200 OK):**
```json
{
  "quick_replies": [
    "Tudo bem, obrigada!",
    "Tenho uma dúvida...",
    "Sinto-me melhor agora",
    "Preciso remarcar"
  ]
}
```

#### POST `/api/v1/messages/:message_id/auto-reply`
Sistema envia auto-resposta (1.8s delay).

**Request:**
```json
{
  "response_text": "Obrigada pela mensagem. A equipe responderá em breve."
}
```

**Response (201 Created):**
```json
{
  "id": "msg_003",
  "sender_type": "system",
  "message_text": "Obrigada pela mensagem. A equipe responderá em breve.",
  "timestamp": "2024-02-15T10:38:00Z",
  "created_at": "2024-02-15T10:38:00Z"
}
```

#### PATCH `/api/v1/messages/:message_id/read`
Marcar mensagem como lida.

**Request:**
```json
{
  "read": true
}
```

**Response (200 OK):**
```json
{
  "id": "msg_001",
  "read": true,
  "read_at": "2024-02-15T10:35:00Z"
}
```

---

### 7. AVISOS/NOTIFICAÇÕES

#### GET `/api/v1/clinics/:clinic_id/announcements`
Listar avisos da clínica.

**Query Parameters:**
- `category`: agenda, saude, clinica, geral (opcional)
- `status`: new, read, all (padrão: all)
- `limit`: número de avisos (padrão: 20)
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 5,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "anc_001",
      "title": "Recesso de Carnaval",
      "description": "A clínica estará fechada durante o Carnaval",
      "category": "clinica",
      "icon": "calendar",
      "date_posted": "2024-02-10T10:00:00Z",
      "date_relative": "5 dias atrás",
      "is_new": true,
      "content": "A clínica estará fechada de 12 a 14 de fevereiro."
    },
    {
      "id": "anc_002",
      "title": "Campanha de Vacinação",
      "description": "Nova campanha de vacinação está disponível",
      "category": "saude",
      "icon": "syringe",
      "date_posted": "2024-02-09T10:00:00Z",
      "date_relative": "6 dias atrás",
      "is_new": true,
      "content": "A campanha de vacinação contra influenza está aberta."
    }
  ]
}
```

#### GET `/api/v1/announcements/:announcement_id`
Obter detalhes de um aviso.

**Response (200 OK):**
```json
{
  "id": "anc_001",
  "title": "Recesso de Carnaval",
  "description": "A clínica estará fechada durante o Carnaval",
  "category": "clinica",
  "icon": "calendar",
  "date_posted": "2024-02-10T10:00:00Z",
  "content": "A clínica estará fechada de 12 a 14 de fevereiro. Funcionaremos normalmente a partir de 15 de fevereiro.",
  "image_url": "https://..."
}
```

#### PATCH `/api/v1/announcements/:announcement_id/read`
Marcar aviso como lido.

**Request:**
```json
{
  "read": true
}
```

**Response (200 OK):**
```json
{
  "id": "anc_001",
  "is_new": false,
  "read_at": "2024-02-15T10:00:00Z"
}
```

#### GET `/api/v1/patients/:patient_id/announcements/unread`
Obter total de avisos não lidos (para badge).

**Response (200 OK):**
```json
{
  "unread_count": 2
}
```

---

### 8. CLÍNICA & EQUIPE

#### GET `/api/v1/clinics/:clinic_id`
Obter informações da clínica.

**Response (200 OK):**
```json
{
  "id": "clinic_456",
  "name": "Clínica Lunna",
  "logo_url": "https://...",
  "primary_color": "#8DAA91",
  "secondary_color": "#E5987D",
  "accent_color": "#E5987D",
  "address": "Rua X, 123, São Paulo, SP",
  "phone": "(11) 3000-0000",
  "email": "contato@lunnaclinica.com.br",
  "website": "https://lunnaclinica.com.br",
  "hours": {
    "monday": "08:00-18:00",
    "tuesday": "08:00-18:00",
    "wednesday": "08:00-18:00",
    "thursday": "08:00-18:00",
    "friday": "08:00-18:00",
    "saturday": "08:00-12:00",
    "sunday": "closed"
  }
}
```

#### GET `/api/v1/clinics/:clinic_id/team`
Listar membros da equipe.

**Query Parameters:**
- `role`: doctor, secretary, all (padrão: all)

**Response (200 OK):**
```json
{
  "total": 5,
  "data": [
    {
      "id": "usr_456",
      "name": "Dra. Ana Lima",
      "role": "doctor",
      "specialty": "Obstetrics",
      "avatar_url": "https://...",
      "crm": "123456",
      "bio": "Especialista em pré-natal"
    },
    {
      "id": "usr_789",
      "name": "Secretária Paula",
      "role": "secretary",
      "avatar_url": "https://...",
      "phone": "(11) 98888-8888"
    }
  ]
}
```

#### GET `/api/v1/doctors/:doctor_id`
Obter perfil do médico.

**Response (200 OK):**
```json
{
  "id": "usr_456",
  "name": "Dra. Ana Lima",
  "role": "doctor",
  "specialty": "Obstetrics",
  "avatar_url": "https://...",
  "crm": "123456",
  "bio": "Especialista em pré-natal",
  "phone": "(11) 99999-9999",
  "email": "ana@lunnaclinica.com.br",
  "clinic_id": "clinic_456"
}
```

#### GET `/api/v1/doctors/:doctor_id/patients`
Listar pacientes do médico.

**Query Parameters:**
- `status`: active, inactive, all (padrão: active)
- `risk_level`: low, medium, high (opcional)
- `limit`: número de pacientes
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 15,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "usr_123",
      "name": "Maria da Silva",
      "avatar_url": "https://...",
      "week_number": 24,
      "risk_level": "low",
      "next_appointment": "2024-02-15T14:30:00Z",
      "status": "active"
    }
  ]
}
```

#### GET `/api/v1/doctors/:doctor_id/patients/search`
Buscar paciente por nome ou prontuário.

**Query Parameters:**
- `q`: termo de busca (nome ou prontuário)

**Response (200 OK):**
```json
{
  "total": 2,
  "data": [
    {
      "id": "usr_123",
      "name": "Maria da Silva",
      "prontuario": "2024-00847",
      "week_number": 24
    }
  ]
}
```

#### GET `/api/v1/doctors/:doctor_id/appointments`
Obter agenda do médico (filtrada por período).

**Query Parameters:**
- `view`: day, week, month (padrão: month)
- `date`: YYYY-MM-DD (data de referência)

**Response (200 OK):**
```json
{
  "doctor_id": "usr_456",
  "view": "day",
  "date": "2024-02-15",
  "appointments": [
    {
      "id": "apt_001",
      "time": "10:00",
      "patient_name": "Maria da Silva",
      "status": "confirmed",
      "type": "routine"
    },
    {
      "id": "apt_002",
      "time": "14:30",
      "patient_name": "João da Silva",
      "status": "pending",
      "type": "ultrasound"
    }
  ]
}
```

#### GET `/api/v1/secretaries/:secretary_id/patients`
Listar pacientes da clínica (para secretária).

**Query Parameters:**
- `search`: termo de busca
- `risk_level`: low, medium, high (opcional)
- `limit`: número de pacientes
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 50,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "usr_123",
      "name": "Maria da Silva",
      "prontuario": "2024-00847",
      "week_number": 24,
      "doctor_name": "Dra. Ana Lima",
      "risk_level": "low",
      "next_appointment": "2024-02-15T14:30:00Z"
    }
  ]
}
```

#### POST `/api/v1/secretaries/:secretary_id/patients`
Cadastrar nova paciente.

**Request:**
```json
{
  "email": "nova@email.com",
  "password": "senha123",
  "name": "Nova Paciente",
  "phone": "(11) 99999-9999",
  "date_of_birth": "1990-05-15",
  "lmp_date": "2023-11-15",
  "doctor_id": "usr_456"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_999",
  "name": "Nova Paciente",
  "email": "nova@email.com",
  "phone": "(11) 99999-9999",
  "prontuario": "2024-00999",
  "doctor_id": "usr_456",
  "created_at": "2024-02-15T10:00:00Z"
}
```

#### POST `/api/v1/secretaries/:secretary_id/reminders`
Enviar lembrete de consulta.

**Request:**
```json
{
  "appointment_id": "apt_001",
  "message_template": "default" // default, custom
}
```

**Response (201 Created):**
```json
{
  "id": "rem_001",
  "appointment_id": "apt_001",
  "patient_id": "usr_123",
  "message": "Lembrete: sua consulta está marcada para 15 de fevereiro às 14:30.",
  "sent_at": "2024-02-15T10:00:00Z"
}
```

#### GET `/api/v1/secretaries/:secretary_id/reports/daily`
Obter relatório do dia.

**Query Parameters:**
- `date`: YYYY-MM-DD (data do relatório)

**Response (200 OK):**
```json
{
  "date": "2024-02-15",
  "total_appointments": 10,
  "confirmed_appointments": 8,
  "pending_appointments": 2,
  "completed_appointments": 5,
  "total_patients": 50,
  "new_patients": 1,
  "summary": {
    "medical_alerts": 2,
    "pending_exams": 3,
    "reminders_sent": 8
  }
}
```

---

### 9. CONTEÚDO (Dicas, Vídeos, Nomes)

#### GET `/api/v1/weeks/:week_number/tips`
Listar dicas para a semana gestacional.

**Response (200 OK):**
```json
{
  "week_number": 24,
  "data": [
    {
      "id": "tip_001",
      "title": "Movimentos do bebê",
      "description": "Você deve sentir movimentos regulares",
      "content": "Por volta da semana 24, você sentirá movimentos claros...",
      "image_url": "https://...",
      "category": "development"
    }
  ]
}
```

#### GET `/api/v1/videos/experts`
Listar vídeos com especialistas.

**Query Parameters:**
- `week`: número da semana (opcional)
- `limit`: número de vídeos (padrão: 10)

**Response (200 OK):**
```json
{
  "total": 5,
  "data": [
    {
      "id": "vid_001",
      "title": "Preparação para o Parto",
      "description": "Como se preparar para o parto",
      "category": "preparation",
      "thumbnail_url": "https://...",
      "professional_name": "Dra. Ana Lima",
      "professional_role": "Obstetric",
      "duration_minutes": 12,
      "video_url": "https://youtube.com/..."
    }
  ]
}
```

#### GET `/api/v1/videos/:video_id`
Obter detalhes do vídeo.

**Response (200 OK):**
```json
{
  "id": "vid_001",
  "title": "Preparação para o Parto",
  "description": "Como se preparar para o parto",
  "category": "preparation",
  "thumbnail_url": "https://...",
  "professional_name": "Dra. Ana Lima",
  "professional_role": "Obstetric",
  "duration_minutes": 12,
  "video_url": "https://youtube.com/...",
  "transcript": "...",
  "created_at": "2024-01-10T10:00:00Z"
}
```

#### GET `/api/v1/baby-names`
Listar nomes de bebês.

**Query Parameters:**
- `gender`: M, F, U (padrão: U para ambos)
- `sort`: popularity, alphabetical, recency (padrão: popularity)
- `limit`: número de nomes (padrão: 100)
- `offset`: paginação

**Response (200 OK):**
```json
{
  "total": 200,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "id": "name_001",
      "name": "João",
      "gender": "M",
      "origin": "Hebraic",
      "meaning": "Deus é gracioso",
      "popularity_rank": 1,
      "popularity_trend": "stable" // stable, rising, declining
    }
  ]
}
```

#### GET `/api/v1/baby-names/:name_id`
Obter detalhes do nome.

**Response (200 OK):**
```json
{
  "id": "name_001",
  "name": "João",
  "gender": "M",
  "origin": "Hebraic",
  "meaning": "Deus é gracioso",
  "popularity_rank": 1,
  "popularity_data": {
    "2015": 15,
    "2016": 18,
    "2017": 20,
    "2018": 22,
    "2019": 25,
    "2020": 28,
    "2021": 30,
    "2022": 32,
    "2023": 35,
    "2024": 38
  },
  "famous_people": ["João Silva", "João Santos"]
}
```

#### POST `/api/v1/patients/:patient_id/favorite-names`
Guardar nome nos favoritos.

**Request:**
```json
{
  "name_id": "name_001"
}
```

**Response (201 Created):**
```json
{
  "id": "fav_001",
  "patient_id": "usr_123",
  "name_id": "name_001",
  "name": "João",
  "saved_at": "2024-02-15T10:00:00Z"
}
```

#### GET `/api/v1/superadmin/clinics`
Listar todas as clínicas do sistema.
**Restrição:** Superadmin apenas.

**Response (200 OK):**
```json
[
  {
    "id": "clinic_456",
    "name": "Clínica Lunna",
    "email": "contato@lunnaclinica.com",
    "created_at": "2024-01-10T10:00:00Z"
  }
]
```

#### POST `/api/v1/superadmin/clinics`
Cadastrar nova clínica e seu administrador inicial.
**Restrição:** Superadmin apenas.

**Request:**
```json
{
  "name": "Nova Clínica",
  "email": "contato@novaclinica.com",
  "admin_email": "admin@novaclinica.com",
  "admin_name": "Admin Principal",
  "admin_password": "senha_segura"
}
```

**Response (201 Created):**
```json
{
  "id": "clinic_789",
  "name": "Nova Clínica",
  "created_at": "2024-02-15T10:00:00Z"
}
```

---

### 10. CONFIGURAÇÕES DO SISTEMA

#### GET `/api/v1/clinics/:clinic_id/settings`
Obter configurações da clínica (white-label).

**Response (200 OK):**
```json
{
  "clinic_id": "clinic_456",
  "logo_url": "https://...",
  "primary_color": "#8DAA91",
  "secondary_color": "#E5987D",
  "accent_color": "#E5987D",
  "theme": "light",
  "language": "pt-BR",
  "timezone": "America/Sao_Paulo"
}
```

#### PUT `/api/v1/clinics/:clinic_id/settings`
Atualizar configurações white-label.

**Request:**
```json
{
  "logo_url": "https://new-logo.jpg",
  "primary_color": "#8DAA91",
  "secondary_color": "#E5987D",
  "accent_color": "#E5987D"
}
```

**Response (200 OK):**
```json
{
  "clinic_id": "clinic_456",
  "logo_url": "https://new-logo.jpg",
  "updated_at": "2024-02-15T10:00:00Z"
}
```

#### GET `/api/v1/system/pregnancy-constants`
Obter constantes do sistema.

**Response (200 OK):**
```json
{
  "total_weeks": 42,
  "trimester_breaks": [
    { "trimester": 1, "weeks": "1-13" },
    { "trimester": 2, "weeks": "14-27" },
    { "trimester": 3, "weeks": "28-42" }
  ],
  "viability_week": 24,
  "normal_glucose_fasting": 95,
  "normal_bp_systolic": 120,
  "normal_bp_diastolic": 80
}
```

---

## Estruturas de Dados

### User (Usuário)

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  password_hash: string; // armazenar com hash bcrypt
  role: "patient" | "doctor" | "secretary" | "admin" | "superadmin";
  clinic_id: string;
  avatar_url?: string;
  phone?: string;
  date_of_birth?: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: timestamp;
  updated_at: timestamp;
}
```

### Patient (Paciente)

```typescript
interface Patient extends User {
  role: "patient";
  prontuario: string;
  lmp_date: string; // last menstrual period
  edd: string; // estimated due date
  current_week: number;
  doctor_id: string; // FK para User(doctor)
}
```

### Doctor (Médico)

```typescript
interface Doctor extends User {
  role: "doctor";
  specialty: string;
  crm: string;
  bio?: string;
  clinic_id: string;
}
```

### Secretary (Secretária)

```typescript
interface Secretary extends User {
  role: "secretary";
  clinic_id: string;
}
```

### Appointment (Consulta)

```typescript
interface Appointment {
  id: string;
  patient_id: string; // FK
  doctor_id: string; // FK
  clinic_id: string; // FK
  date: string; // YYYY-MM-DD
  time: string; // HH:MM
  datetime: timestamp;
  status: "pending" | "confirmed" | "completed" | "cancelled";
  patient_status: "pending" | "confirmed" | "reschedule_requested" | "reschedule_approved";
  type: "routine" | "ultrasound" | "lab" | "other";
  location: string;
  notes?: string;
  duration_minutes: number;
  confirmed_at?: timestamp;
  reschedule_reason?: string;
  reschedule_requested_at?: timestamp;
  reschedule_approved_at?: timestamp;
  created_at: timestamp;
  updated_at: timestamp;
}
```

### VitalSign (Base para sinais vitais)

```typescript
interface VitalSign {
  id: string;
  patient_id: string; // FK
  timestamp: timestamp;
  created_at: timestamp;
  updated_at: timestamp;
}

interface Contraction extends VitalSign {
  duration_seconds: number;
  interval_minutes?: number;
}

interface GlucoseReading extends VitalSign {
  value_mg_dl: number;
  moment: "fasting" | "after_meal" | "random";
  notes?: string;
  classification: "Normal" | "Atenção" | "Alto";
}

interface BloodPressure extends VitalSign {
  systolic: number;
  diastolic: number;
  pulse_bpm?: number;
  moment: "morning" | "afternoon" | "evening" | "night";
  classification: "Normal" | "Atenção" | "Alto";
}
```

### Exam (Exame)

```typescript
interface Ultrasound {
  id: string;
  patient_id: string;
  type: "obstetric" | "morphology" | "detailed";
  date: string;
  ig_weeks: number;
  presentation: "cephalic" | "breech" | "transverse";
  placenta_location?: string;
  amniotic_fluid_ml?: number;
  fetal_heart_rate?: number;
  fetal_weight_g?: number;
  percentile?: number;
  notes?: string;
  image_url?: string;
  created_at: timestamp;
}

interface LabTest {
  id: string;
  patient_id: string;
  date: string;
  hemoglobin?: number;
  hematocrit?: number;
  platelets?: number;
  fasting_glucose?: number;
  tsh?: number;
  ferritin?: number;
  vitamin_d?: number;
  b12?: number;
  eas?: string;
  urine_culture?: string;
  serology: {
    hiv?: string;
    syphilis?: string;
    hepatitis_b?: string;
    hepatitis_c?: string;
    rubella?: string;
    toxoplasmosis?: string;
    cmv?: string;
    herpes?: string;
    group_b_strep?: string;
  };
  notes?: string;
  created_at: timestamp;
}
```

### MedicalRecord (Prontuário)

```typescript
interface MedicalRecord {
  id: string;
  patient_id: string;
  
  identification: {
    baby_name?: string;
    companion?: string;
    hospital?: string;
    risk_classification: "low" | "medium" | "high";
    height_cm: number;
    weight_initial_kg: number;
    imc: number;
    number_of_fetuses: number;
    parity: string;
    risk_factors: string[];
    edd: string;
    cesarean_predicted: boolean;
  };
  
  clinical_data: {
    allergies: string[];
    medications: string[];
    chronic_diseases: string[];
    previous_surgeries: string[];
    gynecological_history?: string;
    family_history?: string;
    occupation?: string;
    habits?: string;
    observations?: string;
  };
  
  special_exams: {
    blood_type: string;
    nipt?: string;
    glucose_curve?: {
      fasting: number;
      one_hour: number;
      two_hours: number;
      status: string;
    };
    group_b_strep?: string;
  };
  
  doctor_notes?: {
    content: string;
    updated_at: timestamp;
    updated_by: string;
  };
  
  created_at: timestamp;
  updated_at: timestamp;
}
```

### Message (Mensagem)

```typescript
interface Message {
  id: string;
  patient_id: string;
  doctor_id?: string;
  sender_type: "patient" | "doctor" | "system";
  message_text: string;
  read: boolean;
  read_at?: timestamp;
  timestamp: timestamp;
  created_at: timestamp;
}
```

### Announcement (Aviso)

```typescript
interface Announcement {
  id: string;
  clinic_id: string;
  title: string;
  description: string;
  content: string;
  category: "agenda" | "saude" | "clinica" | "geral";
  icon: string;
  image_url?: string;
  date_posted: timestamp;
  is_new: boolean;
  created_at: timestamp;
  updated_at: timestamp;
}
```

### Clinic (Clínica)

```typescript
interface Clinic {
  id: string;
  name: string;
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  accent_color?: string;
  address: string;
  phone: string;
  email?: string;
  website?: string;
  hours: {
    monday?: string;
    tuesday?: string;
    wednesday?: string;
    thursday?: string;
    friday?: string;
    saturday?: string;
    sunday?: string;
  };
  created_at: timestamp;
  updated_at: timestamp;
}
```

---

## Padrões RESTful

### Convenções de URL

```
Base: /api/v1/

Recursos:
GET    /users/:id              — Obter usuário
PUT    /users/:id              — Atualizar usuário
DELETE /users/:id              — Deletar usuário

GET    /patients/:id/appointments          — Listar consultas
POST   /patients/:id/appointments          — Criar consulta
GET    /appointments/:id                   — Obter detalhes
PATCH  /appointments/:id/confirm           — Confirmar presença

GET    /patients/:id/glucose-readings      — Listar glicose
POST   /patients/:id/glucose-readings      — Registrar glicose
GET    /patients/:id/glucose-readings/stats — Estatísticas
```

### Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK — Sucesso |
| 201 | Created — Recurso criado |
| 204 | No Content — Deletado sem resposta |
| 400 | Bad Request — Validação falhou |
| 401 | Unauthorized — Não autenticado |
| 403 | Forbidden — Sem permissão |
| 404 | Not Found — Recurso não existe |
| 409 | Conflict — Conflito (ex: email duplicado) |
| 500 | Internal Server Error — Erro do servidor |

### Paginação

```json
Query: ?limit=20&offset=0

Response:
{
  "total": 100,
  "limit": 20,
  "offset": 0,
  "data": [ ... ]
}
```

### Filtros e Ordenação

```
GET /api/v1/patients/:id/appointments?status=confirmed&limit=10&offset=0
GET /api/v1/glucose-readings?days=30&sort=timestamp&order=desc
```

### Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is already registered",
    "details": {
      "field": "email",
      "value": "usuario@clinic.com"
    }
  }
}
```

### Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1644897600
```

---

## Fluxos Principais

### 1. Fluxo de Autenticação e Onboarding

```
1. Usuário acessa /login
2. POST /auth/login com email e senha
3. Sistema retorna JWT access_token + refresh_token
4. Cliente armazena tokens (sessionStorage ou localStorage)
5. GET /users/:user_id para obter perfil
6. Verificar localStorage[onboarded] — se não existe, redirecionar para onboarding
7. POST onboarding → localStorage[onboarded] = true
```

### 2. Fluxo de Consulta com Confirmação de Presença

```
1. Paciente visualiza home.html
2. GET /patients/:id/appointments/next → próxima consulta
3. Paciente clica "Confirmar presença"
4. PATCH /appointments/:id/confirm
5. Estado persistido em localStorage (gv_consulta_proxima_status)
6. GET /appointments/:id → renderiza badge "✓ Presença confirmada"
```

### 3. Fluxo de Remarcação

```
1. Paciente clica "Solicitar remarcação"
2. Abre bottom sheet com 4 chips de motivo selecionáveis
3. POST /appointments/:id/reschedule-request com motivo
4. Estado muda para "⏳ Remarcação solicitada"
5. Médica recebe notificação
6. PATCH /appointments/:id/reschedule/approve com nova_data
7. Paciente notificado da nova data
```

### 4. Fluxo de Monitoramento de Sinais Vitais

```
1. Paciente abre glicose.html
2. GET /patients/:id/glucose-readings/stats → renderiza stats
3. GET /patients/:id/glucose-readings/chart → dados para Canvas
4. FAB clica → abre modal "Registrar Glicose"
5. POST /patients/:id/glucose-readings
6. GET atualiza histórico e gráfico
7. Dados persistem em localStorage (storageKey)
```

### 5. Fluxo de Edição do Cartão Clínico (Médica)

```
1. Médica acessa paciente_detalhe.html
2. GET /patients/:id/medical-record → carrega todas as seções
3. Médica edita Identificação → PATCH /patients/:id/medical-record/identification
4. Médica edita Dados Clínicos → PATCH /patients/:id/medical-record/clinical-data
5. Cada seção tem botão "Salvar alterações" com feedback visual
6. Dados salvos em localStorage (gv_cartao_1498) e sínc com API
7. Timestamps atualizam automaticamente
```

### 6. Fluxo de Chat

```
1. Paciente abre chat.html
2. GET /patients/:id/messages → carrega histórico
3. Paciente digita mensagem
4. POST /patients/:id/messages
5. Cliente renderiza balão à direita
6. Sistema aguarda 1.8s e POST /messages/:id/auto-reply
7. Resposta automática renderizada à esquerda com avatar
8. Médica responde quando disponível
```

### 7. Fluxo de Secretária Criando Agendamento

```
1. Secretária acessa dashboard_secretaria.html
2. FAB "Novo Agendamento"
3. Busca paciente: GET /secretaries/:id/patients?search=termo
4. Seleciona médica disponível
5. POST /doctors/:doctor_id/appointments
6. Agendamento criado com status "pending"
7. Sistema envia notificação à paciente
8. Paciente tem 48h para confirmar presença (PATCH /appointments/:id/confirm)
```

---

## Considerações de Segurança

### Autenticação & Autorização

- **JWT com expiração:** access_token expira em 15 minutos
- **Refresh token:** expira em 7 dias (armazenar com hash no DB)
- **RBAC:** Validar role em cada endpoint protegido
- **Ownershi check:** Paciente só acessa seus próprios dados

```javascript
// Middleware exemplo
function authRequired(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Missing token" });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (e) {
    res.status(401).json({ error: "Invalid token" });
  }
}

function patientOnly(req, res, next) {
  if (req.user.role !== "patient") return res.status(403).json({ error: "Forbidden" });
  
  const patientId = req.params.patient_id;
  if (req.user.id !== patientId) return res.status(403).json({ error: "Forbidden" });
  
  next();
}
```

### Proteção de Dados

- **Senha:** Hash com bcrypt (rounds: 12)
- **Dados sensíveis:** Criptografia em repouso (AES-256)
- **HTTPS obrigatório:** Todas requisições via HTTPS
- **CORS:** Whitelist de domínios permitidos

### Validação & Sanitização

- **Input validation:** usar bibliotecas como `joi`, `zod`, `yup`
- **Output encoding:** escape HTML em todas as respostas
- **SQL Injection:** usar prepared statements (Supabase/Prisma fazem nativamente)
- **XSS:** sanitizar mensagens do chat com DOMPurify ou similar

```javascript
// Exemplo de validação
const appointmentSchema = z.object({
  patient_id: z.string().uuid(),
  date: z.string().date(),
  time: z.string().regex(/^\d{2}:\d{2}$/),
  type: z.enum(["routine", "ultrasound", "lab"]),
  notes: z.string().max(500).optional()
});

// Usar em endpoint
app.post("/appointments", async (req, res) => {
  const validated = appointmentSchema.parse(req.body);
  // ... continuar
});
```

### Auditoria

- **Log de acesso:** Quem, o quê, quando
- **Log de alterações:** Médica altera dados → registrar user_id, timestamp, old_value, new_value
- **Log de sensíveis:** Acesso a notas privadas da médica, mensagens de chat

### Conformidade LGPD/GDPR

- **Direito ao esquecimento:** Endpoint DELETE /users/:id com soft delete
- **Exportação de dados:** GET /users/:id/export → JSON com todos os dados do usuário
- **Consentimento:** Aceitar ToS ao registrar, rastrear em DB

---

## Observações Técnicas

### Versionamento de API

- Sempre versionar: `/api/v1/`, `/api/v2/`, etc.
- Não quebrar versão antiga (manter `/v1` funcionando mesmo ao lançar `/v2`)

### Documentação

- Usar OpenAPI/Swagger: `swagger.json` ou Postman collection
- Manter ATUALIZADO sempre que adicionar endpoint

### Testing

- Unit tests: lógica de classificação (Normal/Atenção/Alto)
- Integration tests: fluxos completos (autenticação → consulta → confirmação)
- E2E tests: aplicação rodando, user registra glicose, vê no histórico

### Performance

- **Indexes:** Criar índices em `patient_id`, `doctor_id`, `clinic_id`, `timestamp`
- **Caching:** GET de dados estáticos (clínica info, team members) com cache 1h
- **Pagination:** Sempre paginar listagens grandes
- **Lazy loading:** Carregar mensagens antigas apenas on-demand

### Deployment

- **CI/CD:** GitHub Actions ou similar
- **Environment:** .env com DB_URL, JWT_SECRET, etc.
- **Migrations:** Usar Supabase migrations para schema changes
- **Monitoring:** Sentry para error tracking, Grafana para métricas

---

**Última atualização:** Fevereiro 2024

**Próximas etapas:** Implementar API em Node.js/Express ou Next.js + Supabase (PostgreSQL)

