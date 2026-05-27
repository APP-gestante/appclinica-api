# Especificação de Banco de Dados — Lunna

**Schema PostgreSQL para Supabase**

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Tipos Customizados (Enums)](#tipos-customizados-enums)
3. [Tabelas Principais](#tabelas-principais)
4. [Relacionamentos (ER Diagram)](#relacionamentos-er-diagram)
5. [Scripts SQL de Criação](#scripts-sql-de-criação)
6. [Índices](#índices)
7. [Row Level Security (RLS)](#row-level-security-rls)
8. [Triggers & Functions](#triggers--functions)
9. [Considerações de Performance](#considerações-de-performance)

---

## Visão Geral

### Stack

- **Banco de Dados:** PostgreSQL (Supabase)
- **ORM (opcional):** Prisma, TypeORM ou Query raw
- **Relacionamentos:** Foreign Keys com ON CASCADE/RESTRICT
- **Segurança:** Row Level Security (RLS) habilitado
- **Versionamento:** Migrations (Supabase migrations ou Prisma migrations)

### Princípios

- Normalização até 3ª Forma Normal (3NF)
- UUIDs como chave primária (via `gen_random_uuid()`)
- Timestamps `created_at`, `updated_at` em todas as tabelas
- Soft deletes onde aplicável (com `deleted_at`)
- Índices em foreign keys e campos frequentemente filtrados

---

## Tipos Customizados (Enums)

### Roles de Usuário

```sql
CREATE TYPE user_role AS ENUM (
  'patient',
  'doctor',
  'secretary',
  'admin'
);
```

### Status de Consulta

```sql
CREATE TYPE appointment_status AS ENUM (
  'pending',
  'confirmed',
  'completed',
  'cancelled'
);
```

### Status de Paciente em Consulta

```sql
CREATE TYPE patient_appointment_status AS ENUM (
  'pending',
  'confirmed',
  'reschedule_requested',
  'reschedule_approved'
);
```

### Tipo de Consulta

```sql
CREATE TYPE appointment_type AS ENUM (
  'routine',
  'ultrasound',
  'lab',
  'follow_up',
  'emergency'
);
```

### Classificação de Risco

```sql
CREATE TYPE risk_level AS ENUM (
  'low',
  'medium',
  'high'
);
```

### Classificação de Sinais Vitais

```sql
CREATE TYPE vital_classification AS ENUM (
  'Normal',
  'Atenção',
  'Alto'
);
```

### Momento do Dia

```sql
CREATE TYPE time_of_day AS ENUM (
  'morning',
  'afternoon',
  'evening',
  'night'
);
```

### Momento de Medição de Glicose

```sql
CREATE TYPE glucose_moment AS ENUM (
  'fasting',
  'after_meal',
  'random'
);
```

### Apresentação Fetal

```sql
CREATE TYPE fetal_presentation AS ENUM (
  'cephalic',
  'breech',
  'transverse'
);
```

### Tipo de Ultrassom

```sql
CREATE TYPE ultrasound_type AS ENUM (
  'obstetric',
  'morphology',
  'detailed'
);
```

### Status de Vacina

```sql
CREATE TYPE vaccine_status AS ENUM (
  'scheduled',
  'completed',
  'missed'
);
```

### Status de Sorologia

```sql
CREATE TYPE serology_status AS ENUM (
  'negative',
  'positive',
  'pending'
);
```

### Status de Grupo B Streptococo

```sql
CREATE TYPE streptococo_status AS ENUM (
  'negative',
  'positive',
  'pending',
  'not_done'
);
```

### Categoria de Aviso

```sql
CREATE TYPE announcement_category AS ENUM (
  'agenda',
  'saude',
  'clinica',
  'geral'
);
```

### Sender Type (Chat)

```sql
CREATE TYPE message_sender_type AS ENUM (
  'patient',
  'doctor',
  'system'
);
```

---

## Tabelas Principais

### 1. USERS (Usuários Base)

Tabela base para todos os usuários (pacientes, médicos, secretárias, admins).

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role NOT NULL DEFAULT 'patient',
  clinic_id UUID NOT NULL, -- FK para clinics
  avatar_url TEXT,
  phone VARCHAR(20),
  date_of_birth DATE,
  is_active BOOLEAN DEFAULT true,
  email_verified BOOLEAN DEFAULT false,
  email_verified_at TIMESTAMP,
  last_login_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_users_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE RESTRICT
);
```

### 2. CLINICS (Clínicas)

Tabela de clínicas (white-label).

```sql
CREATE TABLE clinics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  logo_url TEXT,
  primary_color VARCHAR(7), -- #8DAA91
  secondary_color VARCHAR(7), -- #E5987D
  accent_color VARCHAR(7),
  address VARCHAR(500),
  phone VARCHAR(20),
  email VARCHAR(255),
  website VARCHAR(255),
  
  hours_monday VARCHAR(20), -- "08:00-18:00"
  hours_tuesday VARCHAR(20),
  hours_wednesday VARCHAR(20),
  hours_thursday VARCHAR(20),
  hours_friday VARCHAR(20),
  hours_saturday VARCHAR(20),
  hours_sunday VARCHAR(20),
  
  timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
  language VARCHAR(10) DEFAULT 'pt-BR',
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### 3. PATIENTS (Pacientes - Extended)

Extensão da tabela `users` com dados específicos de gestantes.

```sql
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  doctor_id UUID NOT NULL,
  
  prontuario VARCHAR(20) UNIQUE NOT NULL, -- "2024-00847"
  lmp_date DATE NOT NULL, -- last menstrual period
  edd DATE NOT NULL, -- estimated due date
  current_week SMALLINT, -- calculado dinamicamente
  
  height_cm DECIMAL(5, 2),
  weight_initial_kg DECIMAL(5, 2),
  imc DECIMAL(4, 2),
  
  blood_type VARCHAR(5), -- "O+", "A-"
  
  risk_level risk_level DEFAULT 'low',
  risk_factors TEXT[], -- array de strings
  allergies TEXT[],
  
  acompanhante VARCHAR(255),
  hospital VARCHAR(255),
  
  number_of_fetuses SMALLINT DEFAULT 1,
  parity VARCHAR(10), -- "G2P1"
  cesarean_predicted BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_patients_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_patients_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

### 4. DOCTORS (Médicos - Extended)

Extensão da tabela `users` com dados específicos de médicos.

```sql
CREATE TABLE doctors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  
  specialty VARCHAR(100) NOT NULL, -- "Obstetrics"
  crm VARCHAR(20) UNIQUE NOT NULL, -- Conselho Regional de Medicina
  bio TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_doctors_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);
```

### 5. SECRETARIES (Secretárias - Extended)

Extensão da tabela `users` com dados específicos de secretárias.

```sql
CREATE TABLE secretaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  
  position VARCHAR(100), -- "Receptionist", "Schedule Manager"
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_secretaries_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);
```

### 6. USER_PREFERENCES (Preferências de Usuário)

```sql
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  
  notifications_enabled BOOLEAN DEFAULT true,
  email_notifications BOOLEAN DEFAULT true,
  push_notifications BOOLEAN DEFAULT true,
  sms_notifications BOOLEAN DEFAULT false,
  
  language VARCHAR(10) DEFAULT 'pt-BR',
  theme VARCHAR(20) DEFAULT 'light', -- light, dark
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);
```

---

### 7. APPOINTMENTS (Consultas)

```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  clinic_id UUID NOT NULL,
  
  date DATE NOT NULL,
  time TIME NOT NULL,
  datetime TIMESTAMP NOT NULL, -- Combinação de date + time
  duration_minutes SMALLINT DEFAULT 30,
  
  status appointment_status DEFAULT 'pending',
  patient_status patient_appointment_status DEFAULT 'pending',
  
  type appointment_type DEFAULT 'routine',
  location VARCHAR(255), -- "Sala 302"
  notes TEXT,
  
  -- Confirmação de Presença
  confirmed_at TIMESTAMP,
  
  -- Remarcação
  reschedule_reason VARCHAR(255),
  reschedule_observation TEXT,
  reschedule_requested_at TIMESTAMP,
  reschedule_requested_by UUID, -- FK para users
  
  reschedule_approved_at TIMESTAMP,
  reschedule_approved_by UUID, -- FK para users
  new_date DATE,
  new_time TIME,
  
  -- Cancelamento
  cancelled_at TIMESTAMP,
  cancellation_reason VARCHAR(255),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_appointments_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_appointments_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_appointments_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE RESTRICT,
  CONSTRAINT fk_appointments_reschedule_by FOREIGN KEY (reschedule_requested_by) 
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_appointments_approved_by FOREIGN KEY (reschedule_approved_by) 
    REFERENCES users(id) ON DELETE SET NULL
);
```

---

### 8. CONTRACTIONS (Contrações)

```sql
CREATE TABLE contractions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  
  duration_seconds SMALLINT NOT NULL,
  interval_minutes DECIMAL(5, 2), -- Intervalo desde a contração anterior
  
  session_date DATE NOT NULL, -- Data da sessão
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_contractions_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
```

### 9. GLUCOSE_READINGS (Leituras de Glicose)

```sql
CREATE TABLE glucose_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  
  value_mg_dl DECIMAL(5, 2) NOT NULL,
  moment glucose_moment NOT NULL, -- fasting, after_meal, random
  classification vital_classification NOT NULL, -- Normal, Atenção, Alto
  notes TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_glucose_readings_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
```

### 10. BLOOD_PRESSURE_READINGS (Leituras de Pressão Arterial)

```sql
CREATE TABLE blood_pressure_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  
  systolic SMALLINT NOT NULL, -- 120
  diastolic SMALLINT NOT NULL, -- 80
  pulse_bpm SMALLINT, -- Batidas por minuto (opcional)
  
  moment time_of_day NOT NULL, -- morning, afternoon, evening, night
  classification vital_classification NOT NULL, -- Normal, Atenção, Alto
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_blood_pressure_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
```

---

### 11. ULTRASOUNDS (Ultrassonografias)

```sql
CREATE TABLE ultrasounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL, -- Médico que fez o ultrassom
  
  type ultrasound_type NOT NULL, -- obstetric, morphology, detailed
  date DATE NOT NULL,
  
  ig_weeks SMALLINT NOT NULL, -- Idade gestacional em semanas
  
  presentation fetal_presentation, -- cephalic, breech, transverse
  placenta_location VARCHAR(100),
  amniotic_fluid_ml DECIMAL(7, 2),
  
  fetal_heart_rate SMALLINT, -- BCF (batimento cardíaco fetal)
  fetal_weight_g DECIMAL(7, 2),
  percentile SMALLINT, -- 5, 10, 25, 50, 75, 90, 95
  
  image_url TEXT,
  notes TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_ultrasounds_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_ultrasounds_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

### 12. LAB_TESTS (Exames Laboratoriais)

```sql
CREATE TABLE lab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL, -- Médico que solicitou/registrou
  
  date DATE NOT NULL,
  
  hemoglobin DECIMAL(5, 2),
  hematocrit DECIMAL(5, 2),
  platelets DECIMAL(7, 2),
  
  fasting_glucose DECIMAL(5, 2),
  tsh DECIMAL(5, 2),
  ferritin DECIMAL(7, 2),
  vitamin_d DECIMAL(5, 2),
  b12 DECIMAL(7, 2),
  
  eas VARCHAR(50), -- Exame de urina (normal, alterado)
  urine_culture VARCHAR(50), -- negative, positive, pending
  
  notes TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_lab_tests_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_lab_tests_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

### 13. LAB_TEST_SEROLOGY (Sorologias de Exames Laboratoriais)

```sql
CREATE TABLE lab_test_serology (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lab_test_id UUID NOT NULL,
  
  serology_type VARCHAR(50) NOT NULL, -- hiv, syphilis, hepatitis_b, etc
  status serology_status NOT NULL, -- negative, positive, pending
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_serology_lab_test FOREIGN KEY (lab_test_id) 
    REFERENCES lab_tests(id) ON DELETE CASCADE,
  CONSTRAINT uq_serology_per_test UNIQUE (lab_test_id, serology_type)
);
```

### 14. VACCINES (Vacinas)

```sql
CREATE TABLE vaccines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID, -- Médico que registrou (opcional)
  
  vaccine_type VARCHAR(100) NOT NULL, -- tetanus, influenza, covid19
  date DATE NOT NULL,
  
  dose_number SMALLINT,
  status vaccine_status DEFAULT 'scheduled',
  reactions TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_vaccines_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_vaccines_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE SET NULL
);
```

---

### 15. WEIGHT_EVOLUTION (Evolução do Peso)

```sql
CREATE TABLE weight_evolution (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  
  weight_kg DECIMAL(5, 2) NOT NULL,
  week_number SMALLINT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_weight_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
```

### 16. UTERINE_HEIGHT (Altura Uterina)

```sql
CREATE TABLE uterine_height (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  
  height_cm DECIMAL(5, 2) NOT NULL,
  week_number SMALLINT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_uterine_height_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_uterine_height_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

---

### 17. MEDICAL_RECORDS (Prontuários)

```sql
CREATE TABLE medical_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID UNIQUE NOT NULL,
  
  -- Identificação
  baby_name VARCHAR(255),
  companion VARCHAR(255),
  hospital VARCHAR(255),
  risk_classification risk_level DEFAULT 'low',
  
  -- Dados Clínicos
  allergies TEXT[],
  medications TEXT[],
  chronic_diseases TEXT[],
  previous_surgeries TEXT[],
  gynecological_history TEXT,
  family_history TEXT,
  occupation VARCHAR(100),
  habits VARCHAR(255),
  observations TEXT,
  
  -- Exames Especiais
  nipt VARCHAR(50), -- negative, positive, inconclusive
  group_b_strep streptococo_status DEFAULT 'not_done',
  
  -- Glicose Curve (TOTG)
  glucose_curve_fasting DECIMAL(5, 2),
  glucose_curve_one_hour DECIMAL(5, 2),
  glucose_curve_two_hours DECIMAL(5, 2),
  glucose_curve_status vital_classification,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_medical_records_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
```

### 18. DOCTOR_NOTES (Notas Privadas da Médica)

```sql
CREATE TABLE doctor_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  
  content TEXT NOT NULL,
  is_private BOOLEAN DEFAULT true,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_doctor_notes_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_doctor_notes_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

---

### 19. MESSAGES (Chat)

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID, -- Opcional (null se sender_type != 'doctor')
  
  sender_type message_sender_type NOT NULL, -- patient, doctor, system
  sender_id UUID NOT NULL, -- FK para users
  
  message_text TEXT NOT NULL,
  
  read BOOLEAN DEFAULT false,
  read_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_messages_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_messages_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

---

### 20. ANNOUNCEMENTS (Avisos da Clínica)

```sql
CREATE TABLE announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL,
  created_by UUID NOT NULL, -- FK para users (admin ou secretária)
  
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  content TEXT NOT NULL,
  category announcement_category NOT NULL,
  icon VARCHAR(50), -- Nome do ícone (ex: "calendar", "syringe")
  image_url TEXT,
  
  published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP, -- Opcional: data de expiração
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_announcements_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE CASCADE,
  CONSTRAINT fk_announcements_created_by FOREIGN KEY (created_by) 
    REFERENCES users(id) ON DELETE RESTRICT
);
```

### 21. ANNOUNCEMENT_READS (Rastreamento de Leitura de Avisos)

```sql
CREATE TABLE announcement_reads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  announcement_id UUID NOT NULL,
  user_id UUID NOT NULL,
  
  read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_announcement_reads_announcement FOREIGN KEY (announcement_id) 
    REFERENCES announcements(id) ON DELETE CASCADE,
  CONSTRAINT fk_announcement_reads_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT uq_announcement_user_read UNIQUE (announcement_id, user_id)
);
```

---

### 22. AUDIT_LOG (Log de Auditoria)

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID, -- Usuário que fez a ação (null para sistema)
  action VARCHAR(100) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
  table_name VARCHAR(100) NOT NULL,
  record_id UUID,
  
  old_values JSONB, -- Valores antigos (para UPDATE)
  new_values JSONB, -- Valores novos
  
  ip_address INET,
  user_agent TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_audit_log_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE SET NULL
);
```

---

## Relacionamentos (ER Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLINICS                                    │
│  ┌─────────────┐                                                │
│  │ id (PK)     │                                                │
│  │ name        │                                                │
│  │ logo_url    │                                                │
│  │ colors      │                                                │
│  └─────────────┘                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ (1:N)
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────────┐         ┌──────────────────────┐
│      USERS           │         │  ANNOUNCEMENTS       │
│  ┌─────────────────┐ │         │  ┌─────────────────┐ │
│  │ id (PK)         │ │         │  │ id (PK)         │ │
│  │ email           │ │         │  │ clinic_id (FK)  │ │
│  │ role            │ │         │  │ created_by (FK) │ │
│  │ clinic_id (FK)  │ │         │  │ title           │ │
│  │ password_hash   │ │         │  │ category        │ │
│  └─────────────────┘ │         │  └─────────────────┘ │
└──────┬───────────────┘         └──────────────────────┘
       │ (1:1 extends)
       │
   ┌───┴────────────────────────────────┐
   │                                    │
   ▼                                    ▼
┌─────────────────┐          ┌─────────────────┐
│   PATIENTS      │          │    DOCTORS      │
│  ┌───────────┐  │          │  ┌───────────┐  │
│  │ id (PK)   │  │          │  │ id (PK)   │  │
│  │ user_id   │  │          │  │ user_id   │  │
│  │ doctor_id ├──┼──FK───────├──┤ crm       │  │
│  │ prontuario│  │          │  │ specialty │  │
│  │ risk_level│  │          │  └───────────┘  │
│  └───────────┘  │          └─────────────────┘
└────┬────────────┘
     │ (1:N) Patient -> Appointments
     │       Patient -> Vitals
     │       Patient -> Exams
     │       Patient -> Medical Records
     │
     ├─→ APPOINTMENTS
     ├─→ CONTRACTIONS
     ├─→ GLUCOSE_READINGS
     ├─→ BLOOD_PRESSURE_READINGS
     ├─→ ULTRASOUNDS
     ├─→ LAB_TESTS
     ├─→ VACCINES
     ├─→ WEIGHT_EVOLUTION
     ├─→ UTERINE_HEIGHT
     ├─→ MEDICAL_RECORDS
     ├─→ DOCTOR_NOTES
     └─→ MESSAGES

┌────────────────────────────────────────┐
│        APPOINTMENTS                    │
│  ┌──────────────────────────────────┐  │
│  │ id (PK)                          │  │
│  │ patient_id (FK)                  │  │
│  │ doctor_id (FK)                   │  │
│  │ status, patient_status           │  │
│  │ reschedule_requested_by (FK)     │  │
│  │ reschedule_approved_by (FK)      │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│      VITAL SIGNS (Sinais Vitais)       │
│  ├─ CONTRACTIONS                       │
│  ├─ GLUCOSE_READINGS                   │
│  └─ BLOOD_PRESSURE_READINGS            │
│     (all 1:N from PATIENTS)            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│        EXAMS (Exames)                  │
│  ├─ ULTRASOUNDS                        │
│  ├─ LAB_TESTS                          │
│  │  └─ LAB_TEST_SEROLOGY               │
│  └─ VACCINES                           │
│     (all 1:N from PATIENTS)            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│        DATA EVOLUTION                  │
│  ├─ WEIGHT_EVOLUTION                   │
│  └─ UTERINE_HEIGHT                     │
│     (all 1:N from PATIENTS)            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│     MEDICAL RECORDS & NOTES            │
│  ├─ MEDICAL_RECORDS                    │
│  └─ DOCTOR_NOTES                       │
│     (1:1 and 1:N from PATIENTS)        │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│      MESSAGES (Chat)                   │
│  ┌──────────────────────────────────┐  │
│  │ id (PK)                          │  │
│  │ patient_id (FK)                  │  │
│  │ doctor_id (FK, nullable)         │  │
│  │ sender_id (FK)                   │  │
│  │ sender_type                      │  │
│  │ message_text, read, read_at      │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## Scripts SQL de Criação

### Ordem de Execução

1. Criar tipos (ENUMs)
2. Criar tabelas base (CLINICS, USERS)
3. Criar tabelas extended (PATIENTS, DOCTORS, SECRETARIES)
4. Criar tabelas de relacionamento (APPOINTMENTS, etc.)
5. Criar índices
6. Ativar RLS
7. Criar policies de RLS

### Script Completo

```sql
-- ============================================
-- 1. CREATE CUSTOM TYPES (ENUMS)
-- ============================================

CREATE TYPE user_role AS ENUM ('patient', 'doctor', 'secretary', 'admin', 'superadmin');
CREATE TYPE appointment_status AS ENUM ('pending', 'confirmed', 'completed', 'cancelled');
CREATE TYPE patient_appointment_status AS ENUM ('pending', 'confirmed', 'reschedule_requested', 'reschedule_approved');
CREATE TYPE appointment_type AS ENUM ('routine', 'ultrasound', 'lab', 'follow_up', 'emergency');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high');
CREATE TYPE vital_classification AS ENUM ('Normal', 'Atenção', 'Alto');
CREATE TYPE time_of_day AS ENUM ('morning', 'afternoon', 'evening', 'night');
CREATE TYPE glucose_moment AS ENUM ('fasting', 'after_meal', 'random');
CREATE TYPE fetal_presentation AS ENUM ('cephalic', 'breech', 'transverse');
CREATE TYPE ultrasound_type AS ENUM ('obstetric', 'morphology', 'detailed');
CREATE TYPE vaccine_status AS ENUM ('scheduled', 'completed', 'missed');
CREATE TYPE serology_status AS ENUM ('negative', 'positive', 'pending');
CREATE TYPE streptococo_status AS ENUM ('negative', 'positive', 'pending', 'not_done');
CREATE TYPE announcement_category AS ENUM ('agenda', 'saude', 'clinica', 'geral');
CREATE TYPE message_sender_type AS ENUM ('patient', 'doctor', 'system');

-- ============================================
-- 2. CREATE BASE TABLES
-- ============================================

-- CLINICS
CREATE TABLE clinics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  logo_url TEXT,
  primary_color VARCHAR(7),
  secondary_color VARCHAR(7),
  accent_color VARCHAR(7),
  address VARCHAR(500),
  phone VARCHAR(20),
  email VARCHAR(255),
  website VARCHAR(255),
  hours_monday VARCHAR(20),
  hours_tuesday VARCHAR(20),
  hours_wednesday VARCHAR(20),
  hours_thursday VARCHAR(20),
  hours_friday VARCHAR(20),
  hours_saturday VARCHAR(20),
  hours_sunday VARCHAR(20),
  timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
  language VARCHAR(10) DEFAULT 'pt-BR',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);

-- USERS
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role NOT NULL DEFAULT 'patient',
  clinic_id UUID NOT NULL,
  avatar_url TEXT,
  phone VARCHAR(20),
  date_of_birth DATE,
  is_active BOOLEAN DEFAULT true,
  email_verified BOOLEAN DEFAULT false,
  email_verified_at TIMESTAMP,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_users_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE RESTRICT
);

-- USER_PREFERENCES
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  notifications_enabled BOOLEAN DEFAULT true,
  email_notifications BOOLEAN DEFAULT true,
  push_notifications BOOLEAN DEFAULT true,
  sms_notifications BOOLEAN DEFAULT false,
  language VARCHAR(10) DEFAULT 'pt-BR',
  theme VARCHAR(20) DEFAULT 'light',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 3. CREATE EXTENDED TABLES (Patients, Doctors, Secretaries)
-- ============================================

-- PATIENTS
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  doctor_id UUID NOT NULL,
  prontuario VARCHAR(20) UNIQUE NOT NULL,
  lmp_date DATE NOT NULL,
  edd DATE NOT NULL,
  current_week SMALLINT,
  height_cm DECIMAL(5, 2),
  weight_initial_kg DECIMAL(5, 2),
  imc DECIMAL(4, 2),
  blood_type VARCHAR(5),
  risk_level risk_level DEFAULT 'low',
  risk_factors TEXT[],
  allergies TEXT[],
  acompanhante VARCHAR(255),
  hospital VARCHAR(255),
  number_of_fetuses SMALLINT DEFAULT 1,
  parity VARCHAR(10),
  cesarean_predicted BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_patients_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_patients_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- DOCTORS
CREATE TABLE doctors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  specialty VARCHAR(100) NOT NULL,
  crm VARCHAR(20) UNIQUE NOT NULL,
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_doctors_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);

-- SECRETARIES
CREATE TABLE secretaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  position VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_secretaries_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 4. CREATE APPOINTMENTS & SCHEDULING TABLES
-- ============================================

-- APPOINTMENTS
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  clinic_id UUID NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  datetime TIMESTAMP NOT NULL,
  duration_minutes SMALLINT DEFAULT 30,
  status appointment_status DEFAULT 'pending',
  patient_status patient_appointment_status DEFAULT 'pending',
  type appointment_type DEFAULT 'routine',
  location VARCHAR(255),
  notes TEXT,
  confirmed_at TIMESTAMP,
  reschedule_reason VARCHAR(255),
  reschedule_observation TEXT,
  reschedule_requested_at TIMESTAMP,
  reschedule_requested_by UUID,
  reschedule_approved_at TIMESTAMP,
  reschedule_approved_by UUID,
  new_date DATE,
  new_time TIME,
  cancelled_at TIMESTAMP,
  cancellation_reason VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_appointments_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_appointments_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_appointments_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE RESTRICT,
  CONSTRAINT fk_appointments_reschedule_by FOREIGN KEY (reschedule_requested_by) 
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_appointments_approved_by FOREIGN KEY (reschedule_approved_by) 
    REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 5. CREATE VITAL SIGNS TABLES
-- ============================================

-- CONTRACTIONS
CREATE TABLE contractions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  duration_seconds SMALLINT NOT NULL,
  interval_minutes DECIMAL(5, 2),
  session_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_contractions_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);

-- GLUCOSE_READINGS
CREATE TABLE glucose_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  value_mg_dl DECIMAL(5, 2) NOT NULL,
  moment glucose_moment NOT NULL,
  classification vital_classification NOT NULL,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_glucose_readings_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);

-- BLOOD_PRESSURE_READINGS
CREATE TABLE blood_pressure_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  systolic SMALLINT NOT NULL,
  diastolic SMALLINT NOT NULL,
  pulse_bpm SMALLINT,
  moment time_of_day NOT NULL,
  classification vital_classification NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_blood_pressure_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);

-- ============================================
-- 6. CREATE EXAMS TABLES
-- ============================================

-- ULTRASOUNDS
CREATE TABLE ultrasounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  type ultrasound_type NOT NULL,
  date DATE NOT NULL,
  ig_weeks SMALLINT NOT NULL,
  presentation fetal_presentation,
  placenta_location VARCHAR(100),
  amniotic_fluid_ml DECIMAL(7, 2),
  fetal_heart_rate SMALLINT,
  fetal_weight_g DECIMAL(7, 2),
  percentile SMALLINT,
  image_url TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_ultrasounds_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_ultrasounds_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- LAB_TESTS
CREATE TABLE lab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  date DATE NOT NULL,
  hemoglobin DECIMAL(5, 2),
  hematocrit DECIMAL(5, 2),
  platelets DECIMAL(7, 2),
  fasting_glucose DECIMAL(5, 2),
  tsh DECIMAL(5, 2),
  ferritin DECIMAL(7, 2),
  vitamin_d DECIMAL(5, 2),
  b12 DECIMAL(7, 2),
  eas VARCHAR(50),
  urine_culture VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_lab_tests_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_lab_tests_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- LAB_TEST_SEROLOGY
CREATE TABLE lab_test_serology (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lab_test_id UUID NOT NULL,
  serology_type VARCHAR(50) NOT NULL,
  status serology_status NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_serology_lab_test FOREIGN KEY (lab_test_id) 
    REFERENCES lab_tests(id) ON DELETE CASCADE,
  CONSTRAINT uq_serology_per_test UNIQUE (lab_test_id, serology_type)
);

-- VACCINES
CREATE TABLE vaccines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID,
  vaccine_type VARCHAR(100) NOT NULL,
  date DATE NOT NULL,
  dose_number SMALLINT,
  status vaccine_status DEFAULT 'scheduled',
  reactions TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_vaccines_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_vaccines_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 7. CREATE DATA EVOLUTION TABLES
-- ============================================

-- WEIGHT_EVOLUTION
CREATE TABLE weight_evolution (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  weight_kg DECIMAL(5, 2) NOT NULL,
  week_number SMALLINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_weight_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);

-- UTERINE_HEIGHT
CREATE TABLE uterine_height (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  height_cm DECIMAL(5, 2) NOT NULL,
  week_number SMALLINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_uterine_height_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_uterine_height_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- ============================================
-- 8. CREATE MEDICAL RECORDS & NOTES TABLES
-- ============================================

-- MEDICAL_RECORDS
CREATE TABLE medical_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID UNIQUE NOT NULL,
  baby_name VARCHAR(255),
  companion VARCHAR(255),
  hospital VARCHAR(255),
  risk_classification risk_level DEFAULT 'low',
  allergies TEXT[],
  medications TEXT[],
  chronic_diseases TEXT[],
  previous_surgeries TEXT[],
  gynecological_history TEXT,
  family_history TEXT,
  occupation VARCHAR(100),
  habits VARCHAR(255),
  observations TEXT,
  nipt VARCHAR(50),
  group_b_strep streptococo_status DEFAULT 'not_done',
  glucose_curve_fasting DECIMAL(5, 2),
  glucose_curve_one_hour DECIMAL(5, 2),
  glucose_curve_two_hours DECIMAL(5, 2),
  glucose_curve_status vital_classification,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_medical_records_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);

-- DOCTOR_NOTES
CREATE TABLE doctor_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID NOT NULL,
  content TEXT NOT NULL,
  is_private BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_doctor_notes_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_doctor_notes_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- ============================================
-- 9. CREATE COMMUNICATION TABLES
-- ============================================

-- MESSAGES
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL,
  doctor_id UUID,
  sender_type message_sender_type NOT NULL,
  sender_id UUID NOT NULL,
  message_text TEXT NOT NULL,
  read BOOLEAN DEFAULT false,
  read_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_messages_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE,
  CONSTRAINT fk_messages_doctor FOREIGN KEY (doctor_id) 
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- ============================================
-- 10. CREATE ANNOUNCEMENTS TABLES
-- ============================================

-- ANNOUNCEMENTS
CREATE TABLE announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL,
  created_by UUID NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  content TEXT NOT NULL,
  category announcement_category NOT NULL,
  icon VARCHAR(50),
  image_url TEXT,
  published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT fk_announcements_clinic FOREIGN KEY (clinic_id) 
    REFERENCES clinics(id) ON DELETE CASCADE,
  CONSTRAINT fk_announcements_created_by FOREIGN KEY (created_by) 
    REFERENCES users(id) ON DELETE RESTRICT
);

-- ANNOUNCEMENT_READS
CREATE TABLE announcement_reads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  announcement_id UUID NOT NULL,
  user_id UUID NOT NULL,
  read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_announcement_reads_announcement FOREIGN KEY (announcement_id) 
    REFERENCES announcements(id) ON DELETE CASCADE,
  CONSTRAINT fk_announcement_reads_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT uq_announcement_user_read UNIQUE (announcement_id, user_id)
);

-- ============================================
-- 11. CREATE AUDIT LOG TABLE
-- ============================================

-- AUDIT_LOG
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  action VARCHAR(100) NOT NULL,
  table_name VARCHAR(100) NOT NULL,
  record_id UUID,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_audit_log_user FOREIGN KEY (user_id) 
    REFERENCES users(id) ON DELETE SET NULL
);
```

---

## Índices

### Índices Críticos para Performance

```sql
-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Users
CREATE INDEX idx_users_clinic_id ON users(clinic_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;

-- Patients
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_doctor_id ON patients(doctor_id);
CREATE INDEX idx_patients_prontuario ON patients(prontuario);
CREATE INDEX idx_patients_clinic ON patients(user_id) USING (SELECT clinic_id FROM users WHERE id = patients.user_id);

-- Appointments
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_clinic_id ON appointments(clinic_id);
CREATE INDEX idx_appointments_datetime ON appointments(datetime);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_patient_status ON appointments(patient_status);
CREATE INDEX idx_appointments_date ON appointments(date);

-- Vital Signs
CREATE INDEX idx_contractions_patient_id ON contractions(patient_id);
CREATE INDEX idx_contractions_date ON contractions(session_date);
CREATE INDEX idx_glucose_patient_id ON glucose_readings(patient_id);
CREATE INDEX idx_glucose_created_at ON glucose_readings(created_at);
CREATE INDEX idx_blood_pressure_patient_id ON blood_pressure_readings(patient_id);
CREATE INDEX idx_blood_pressure_created_at ON blood_pressure_readings(created_at);

-- Exams
CREATE INDEX idx_ultrasounds_patient_id ON ultrasounds(patient_id);
CREATE INDEX idx_ultrasounds_doctor_id ON ultrasounds(doctor_id);
CREATE INDEX idx_ultrasounds_date ON ultrasounds(date);
CREATE INDEX idx_lab_tests_patient_id ON lab_tests(patient_id);
CREATE INDEX idx_lab_tests_doctor_id ON lab_tests(doctor_id);
CREATE INDEX idx_lab_tests_date ON lab_tests(date);
CREATE INDEX idx_vaccines_patient_id ON vaccines(patient_id);

-- Data Evolution
CREATE INDEX idx_weight_evolution_patient_id ON weight_evolution(patient_id);
CREATE INDEX idx_weight_evolution_week ON weight_evolution(week_number);
CREATE INDEX idx_uterine_height_patient_id ON uterine_height(patient_id);
CREATE INDEX idx_uterine_height_week ON uterine_height(week_number);

-- Medical Records
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_doctor_notes_patient_id ON doctor_notes(patient_id);
CREATE INDEX idx_doctor_notes_doctor_id ON doctor_notes(doctor_id);

-- Messages
CREATE INDEX idx_messages_patient_id ON messages(patient_id);
CREATE INDEX idx_messages_doctor_id ON messages(doctor_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_read ON messages(read);

-- Announcements
CREATE INDEX idx_announcements_clinic_id ON announcements(clinic_id);
CREATE INDEX idx_announcements_category ON announcements(category);
CREATE INDEX idx_announcements_published_at ON announcements(published_at);
CREATE INDEX idx_announcement_reads_user_id ON announcement_reads(user_id);
CREATE INDEX idx_announcement_reads_announcement_id ON announcement_reads(announcement_id);

-- Audit
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

---

## Row Level Security (RLS)

### Ativar RLS

```sql
-- ============================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE glucose_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE blood_pressure_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ultrasounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
```

### RLS Policies (Exemplos)

```sql
-- ============================================
-- SAMPLE RLS POLICIES
-- ============================================

-- USERS: Cada usuário vê apenas seus próprios dados
CREATE POLICY "Users can see their own profile" 
  ON users FOR SELECT 
  USING (auth.uid()::uuid = id);

CREATE POLICY "Users can update their own profile" 
  ON users FOR UPDATE 
  USING (auth.uid()::uuid = id);

-- PATIENTS: Paciente vê seus próprios dados
CREATE POLICY "Patients can see their own data" 
  ON patients FOR SELECT 
  USING (auth.uid()::uuid = user_id);

-- PATIENTS: Médico vê dados de seus pacientes
CREATE POLICY "Doctors can see their patients" 
  ON patients FOR SELECT 
  USING (auth.uid()::uuid = doctor_id);

-- APPOINTMENTS: Paciente vê suas próprias consultas
CREATE POLICY "Patients can see their appointments" 
  ON appointments FOR SELECT 
  USING (
    auth.uid()::uuid IN (
      SELECT user_id FROM patients WHERE id = appointments.patient_id
    )
  );

-- APPOINTMENTS: Médico vê consultas de seus pacientes
CREATE POLICY "Doctors can see their patients' appointments" 
  ON appointments FOR SELECT 
  USING (auth.uid()::uuid = doctor_id);

-- GLUCOSE: Paciente vê suas próprias leituras
CREATE POLICY "Patients can see their glucose readings" 
  ON glucose_readings FOR SELECT 
  USING (
    auth.uid()::uuid IN (
      SELECT user_id FROM patients WHERE id = glucose_readings.patient_id
    )
  );

-- DOCTOR_NOTES: Apenas médico vê suas notas privadas
CREATE POLICY "Doctors can see their own notes" 
  ON doctor_notes FOR SELECT 
  USING (auth.uid()::uuid = doctor_id);

-- MESSAGES: Paciente/Médico vê suas próprias mensagens
CREATE POLICY "Patients can see their messages" 
  ON messages FOR SELECT 
  USING (
    auth.uid()::uuid IN (
      SELECT user_id FROM patients WHERE id = messages.patient_id
    )
    OR
    auth.uid()::uuid = doctor_id
  );

-- ANNOUNCEMENTS: Qualquer usuário da clínica vê avisos
CREATE POLICY "Clinic users can see announcements" 
  ON announcements FOR SELECT 
  USING (
    clinic_id = (
      SELECT clinic_id FROM users WHERE id = auth.uid()::uuid
    )
  );
```

---

## Triggers & Functions

### Função para Atualizar `updated_at`

```sql
-- ============================================
-- TRIGGERS FOR updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar em todas as tabelas
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_glucose_readings_updated_at BEFORE UPDATE ON glucose_readings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blood_pressure_updated_at BEFORE UPDATE ON blood_pressure_readings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ... (aplicar em outras tabelas conforme necessário)
```

### Função para Audit Log

```sql
-- ============================================
-- TRIGGER FOR AUDIT LOG
-- ============================================

CREATE OR REPLACE FUNCTION audit_log_trigger()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_log (
      user_id,
      action,
      table_name,
      record_id,
      old_values,
      new_values,
      created_at
    ) VALUES (
      auth.uid()::uuid,
      'UPDATE',
      TG_TABLE_NAME,
      NEW.id,
      row_to_json(OLD),
      row_to_json(NEW),
      CURRENT_TIMESTAMP
    );
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log (
      user_id,
      action,
      table_name,
      record_id,
      old_values,
      created_at
    ) VALUES (
      auth.uid()::uuid,
      'DELETE',
      TG_TABLE_NAME,
      OLD.id,
      row_to_json(OLD),
      CURRENT_TIMESTAMP
    );
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log (
      user_id,
      action,
      table_name,
      record_id,
      new_values,
      created_at
    ) VALUES (
      auth.uid()::uuid,
      'INSERT',
      TG_TABLE_NAME,
      NEW.id,
      row_to_json(NEW),
      CURRENT_TIMESTAMP
    );
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Aplicar em tabelas sensíveis
CREATE TRIGGER audit_patients AFTER INSERT OR UPDATE OR DELETE ON patients
  FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_appointments AFTER INSERT OR UPDATE OR DELETE ON appointments
  FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_doctor_notes AFTER INSERT OR UPDATE OR DELETE ON doctor_notes
  FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_lab_tests AFTER INSERT OR UPDATE OR DELETE ON lab_tests
  FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();
```

### Função para Calcular Semana Gestacional

```sql
-- ============================================
-- FUNCTION TO CALCULATE GESTATIONAL WEEK
-- ============================================

CREATE OR REPLACE FUNCTION calculate_gestational_week(lmp_date DATE)
RETURNS SMALLINT AS $$
BEGIN
  RETURN FLOOR((CURRENT_DATE - lmp_date) / 7)::SMALLINT;
END;
$$ LANGUAGE plpgsql;

-- Usar em trigger para atualizar patients.current_week
CREATE OR REPLACE FUNCTION update_gestational_week()
RETURNS TRIGGER AS $$
BEGIN
  NEW.current_week = calculate_gestational_week(NEW.lmp_date);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_gestational_week_patients BEFORE INSERT OR UPDATE ON patients
  FOR EACH ROW EXECUTE FUNCTION update_gestational_week();
```

---

## Considerações de Performance

### Otimizações Implementadas

1. **Índices estratégicos:** Em FKs, timestamps, status
2. **Particionamento (futuro):** `appointments` e `messages` por `clinic_id`
3. **Materialized Views (futuro):** Para dashboards pesados
4. **Caching:** Redis para stats frequentes

### Queries Comuns e Otimizadas

```sql
-- Lista de consultas próximas da paciente
SELECT a.* 
FROM appointments a
JOIN patients p ON a.patient_id = p.id
WHERE p.user_id = $1 
  AND a.datetime > NOW()
  AND a.status != 'cancelled'
ORDER BY a.datetime ASC
LIMIT 5;

-- Histórico de glicose dos últimos 30 dias
SELECT gr.* 
FROM glucose_readings gr
WHERE gr.patient_id = $1 
  AND gr.created_at > NOW() - INTERVAL '30 days'
ORDER BY gr.created_at DESC;

-- Pacientes por risco da médica
SELECT p.*, u.name, u.avatar_url
FROM patients p
JOIN users u ON p.user_id = u.id
WHERE p.doctor_id = $1
  AND p.risk_level = 'high'
  AND p.deleted_at IS NULL
ORDER BY p.updated_at DESC;

-- Total de consultas confirmadas de hoje
SELECT COUNT(*)
FROM appointments
WHERE clinic_id = $1
  AND DATE(datetime) = CURRENT_DATE
  AND patient_status = 'confirmed'
  AND status != 'cancelled';
```

### Monitoramento de Performance

```sql
-- Ver tamanho das tabelas
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver índices e sua utilização
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Checklist de Implementação

- [ ] Criar ENUMs
- [ ] Criar tabelas base (CLINICS, USERS)
- [ ] Criar tabelas extended (PATIENTS, DOCTORS, SECRETARIES)
- [ ] Criar outras tabelas (APPOINTMENTS, VITALS, EXAMS, etc.)
- [ ] Criar índices
- [ ] Ativar RLS
- [ ] Criar RLS policies
- [ ] Criar triggers para `updated_at`
- [ ] Criar trigger para audit log
- [ ] Criar funções de cálculo (semana gestacional, etc.)
- [ ] Testar permissões RLS
- [ ] Testar performance com dados de exemplo
- [ ] Documentar custom types e functions

---

**Última atualização:** Fevereiro 2024

**Próximas etapas:** Executar script SQL no Supabase e configurar RLS policies

