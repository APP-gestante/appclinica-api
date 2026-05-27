# API v2 — Backlog e Status de Integração

Documento vivo de integração entre `lunna-api` e `lunna-app` (GerarVida).  
Atualizado após cada fase de implementação.

Base URL: `http://<host>/api/v1`

**Legenda de status:**
- ✅ **Implementado** — disponível no banco; requer `alembic upgrade head`
- ⏳ **Pendente** — especificado, não implementado ainda
- 🔴 Alta prioridade · 🟡 Média · 🔵 Baixa

---

## Índice rápido

| Feature | Status | Rotas |
|---|---|---|
| Exames laboratoriais | ✅ | `GET/POST /patients/{id}/lab-tests`, `GET /lab-tests/{id}` |
| Medicamentos | ✅ | `GET/POST /patients/{id}/medications`, `PATCH /medications/{id}` |
| Agendamento por paciente | ✅ | `POST /patients/{id}/appointments` |
| Relatório diário | ✅ | `GET /clinics/{id}/reports/daily` |
| Onboarding flag | ✅ | `PATCH /users/{id}/onboarding` |
| Push token | ✅ | `PATCH /users/{id}/push-token` |
| Chat / Mensagens | ⏳ 🔴 | `GET/POST /patients/{id}/messages` + WebSocket |
| Notificações | ⏳ 🟡 | `GET /users/{id}/notifications`, `PATCH /notifications/{id}/read` |
| Lembretes | ⏳ 🟡 | `POST /patients/{id}/reminders` |
| Avisos — detalhe + lido | ⏳ 🟡 | `GET/PATCH /clinics/{id}/announcements/{id}[/read]` |
| Nomes de bebê | ⏳ 🔵 | 4 rotas |
| Desenvolvimento fetal | ⏳ 🔵 | `GET /fetal-development/{week}` |

---

## Migration obrigatória (Fase 1)

Antes de usar qualquer endpoint ✅ desta fase, aplique:

```bash
alembic upgrade head
```

Migração `b1c2d3e4f5a6` cria:  
- Tabela `lab_tests`  
- Tabela `medications`  
- Coluna `push_token` em `users`  
- Coluna `onboarding_completed` em `users`

---

## ✅ Exames Laboratoriais

**Tela mobile:** `AreaMedicaScreen` — aba "Exames"  
**RBAC:** leitura aberta a qualquer usuário autenticado; escrita requer `doctor` ou `admin`

### `GET /patients/{patient_id}/lab-tests`

```
Authorization: Bearer <token>
```

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `type` | string | — | Filtro: `hemograma`, `glicemia`, `urina`, `outros` |
| `limit` | int | 20 | Máximo de itens (até 100) |
| `offset` | int | 0 | Paginação |

**Resposta 200:**
```json
{
  "total": 8,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "patient_id": "<uuid>",
      "doctor_id": "<uuid>",
      "type": "hemograma",
      "name": "Hemograma Completo",
      "date": "2024-03-10",
      "result": "Normal",
      "reference_range": "Hb: 12–16 g/dL",
      "status": "completed",
      "file_url": null,
      "notes": null,
      "created_at": "2024-03-10T14:00:00Z",
      "updated_at": "2024-03-10T14:00:00Z"
    }
  ]
}
```

### `POST /patients/{patient_id}/lab-tests`

**Requer:** `doctor` ou `admin`

**Body:**
```json
{
  "type": "hemograma",
  "name": "Hemograma Completo",
  "date": "2024-03-10",
  "result": "Normal",
  "reference_range": "Hb: 12–16 g/dL",
  "status": "completed",
  "file_url": null,
  "notes": null
}
```

Valores válidos para `type`: `hemograma` · `glicemia` · `urina` · `outros`  
Valores válidos para `status`: `pending` · `completed` · `abnormal`

**Resposta 201:** objeto `LabTestResponse` (mesmo formato do item do GET)

### `GET /lab-tests/{lab_test_id}`

Detalhe de um exame. Qualquer usuário autenticado.

**Resposta 200:** objeto `LabTestResponse`  
**Erros:** `404` se não encontrado

---

## ✅ Medicamentos / Prescrições

**Tela mobile:** `AreaMedicaScreen` — aba "Medicamentos"  
**RBAC:** leitura aberta; `POST` e `PATCH` requerem `doctor` ou `admin`

### `GET /patients/{patient_id}/medications`

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `active` | bool | — | `true` = apenas ativos; `false` = apenas inativos |
| `limit` | int | 20 | — |
| `offset` | int | 0 | — |

**Resposta 200:**
```json
{
  "total": 3,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "patient_id": "<uuid>",
      "doctor_id": "<uuid>",
      "name": "Ácido Fólico",
      "dosage": "5mg",
      "frequency": "1x ao dia",
      "start_date": "2024-01-01",
      "end_date": null,
      "instructions": "Tomar com água, antes do café",
      "active": true,
      "created_at": "2024-01-01T08:00:00Z",
      "updated_at": "2024-01-01T08:00:00Z"
    }
  ]
}
```

### `POST /patients/{patient_id}/medications`

**Requer:** `doctor` ou `admin`

**Body:**
```json
{
  "name": "Sulfato Ferroso",
  "dosage": "40mg",
  "frequency": "2x ao dia",
  "start_date": "2024-03-01",
  "end_date": null,
  "instructions": "Tomar longe das refeições"
}
```

**Resposta 201:** objeto `MedicationResponse`

### `PATCH /medications/{medication_id}`

**Requer:** `doctor` ou `admin`. Todos os campos são opcionais (partial update).

**Body:**
```json
{
  "active": false,
  "end_date": "2024-04-01",
  "dosage": "20mg",
  "frequency": "1x ao dia",
  "instructions": "Redução gradual"
}
```

**Resposta 200:** objeto `MedicationResponse` atualizado  
**Erros:** `404` se não encontrado

---

## ✅ Agendamento por Paciente

**Tela mobile:** `PacienteDetalheScreen` — botão "Agendar consulta"  
**RBAC:** `doctor`, `secretary`, `admin`

### `POST /patients/{patient_id}/appointments`

Alternativa a `POST /doctors/{id}/appointments` — o `patient_id` vem da URL; o `doctor_id` vai no body.

**Body:**
```json
{
  "doctor_id": "<uuid>",
  "date": "2024-04-10",
  "time": "14:30:00",
  "duration_minutes": 30,
  "type": "routine",
  "location": "Consultório 1",
  "notes": null
}
```

Valores válidos para `type`: `routine` · `ultrasound` · `lab` · `follow_up` · `emergency`

**Resposta 201:** objeto `AppointmentResponse`

---

## ✅ Relatório Diário

**Tela mobile:** ação "Relatório do Dia" no dashboard da secretária  
**RBAC:** `secretary`, `admin`

### `GET /clinics/{clinic_id}/reports/daily`

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `date` | string | hoje | Data no formato `YYYY-MM-DD` |

**Resposta 200:**
```json
{
  "date": "2024-03-15",
  "total_appointments": 12,
  "completed": 10,
  "cancelled": 1,
  "no_show": 0,
  "new_patients": 2
}
```

---

## ✅ Onboarding Flag

**Tela mobile:** `OnboardingScreen` — chamar após o usuário concluir o onboarding

### `PATCH /users/{user_id}/onboarding`

```
Authorization: Bearer <token>
```

**Body:**
```json
{ "completed": true }
```

**Resposta 200:** objeto `UserResponse` com `onboarding_completed: true`

**Integração no app:**
```ts
// Após último slide do onboarding:
await api.patch(`/users/${user.id}/onboarding`, { completed: true });
await AsyncStorage.setItem('gv_onboarding_done', 'true');
```

---

## ✅ Push Token (pré-requisito para Notificações e Lembretes)

Registra o Expo push token do dispositivo. Deve ser chamado logo após o login bem-sucedido.

### `PATCH /users/{user_id}/push-token`

```
Authorization: Bearer <token>
```

**Body:**
```json
{ "push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]" }
```

**Resposta 200:** objeto `UserResponse`

**Integração no app (chamar após login):**
```ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

async function registerPushToken(userId: string) {
  if (!Device.isDevice) return; // Simuladores não suportam push
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') return;
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  await api.patch(`/users/${userId}/push-token`, { push_token: token });
}
```

---

---

## ⏳ 🔴 Chat / Mensagens — WebSocket + HTTP

**Tela mobile:** `ChatScreen`  
**Arquitetura definida:** WebSocket nativo FastAPI + Redis Pub/Sub (multi-worker)  
**Modelo necessário:** `Message` (nova migration)

### HTTP — Histórico e envio

#### `GET /patients/{patient_id}/messages`

Lista histórico paginado. Use `before_id` para carregar mensagens mais antigas (cursor reverso).

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int | 30 | — |
| `offset` | int | 0 | — |
| `before_id` | uuid | — | Retorna mensagens anteriores a este ID |

**Resposta 200:**
```json
{
  "total": 45,
  "limit": 30,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "patient_id": "<uuid>",
      "sender_id": "<uuid>",
      "sender_role": "doctor",
      "sender_name": "Dra. Ana Lima",
      "content": "Seus exames estão ótimos!",
      "read": false,
      "created_at": "2024-03-15T10:00:00Z"
    }
  ]
}
```

#### `POST /patients/{patient_id}/messages`

Envia mensagem via HTTP (alternativa ao WS, útil para notificação offline).

**Body:**
```json
{ "content": "Dra, tenho uma dúvida sobre a dieta." }
```

**Resposta 201:** objeto `MessageResponse`

#### `PATCH /patients/{patient_id}/messages/read`

Marca todas as mensagens não lidas como lidas para o usuário autenticado.

**Resposta 200:**
```json
{ "updated": 3 }
```

---

### WebSocket — Tempo real

#### `WS /patients/{patient_id}/ws/chat?token=<access_token>`

> O header `Authorization` não é suportado em conexões WebSocket. O token JWT deve ir no query param `token`.

**Protocolo:**

1. App abre conexão: `ws://api/api/v1/patients/<uuid>/ws/chat?token=<jwt>`
2. Servidor valida token e registra conexão
3. App envia mensagem:
```json
{ "content": "Olá Dra., tudo bem?" }
```
4. Servidor persiste no banco, publica no Redis `chat:<patient_id>`, e retransmite para todas as conexões abertas do mesmo `patient_id`
5. Todos os clientes conectados (paciente + médico) recebem:
```json
{
  "id": "<uuid>",
  "sender_id": "<uuid>",
  "sender_role": "patient",
  "sender_name": "Maria da Silva",
  "content": "Olá Dra., tudo bem?",
  "created_at": "2024-03-15T10:05:00Z"
}
```
6. App deve reconectar automaticamente ao perder conexão (back-off exponencial recomendado)

**Integração no app (exemplo com `expo-websocket` ou WebSocket nativo):**
```ts
const ws = new WebSocket(
  `${WS_BASE_URL}/patients/${patientId}/ws/chat?token=${accessToken}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  setMessages(prev => [message, ...prev]);
};

ws.onclose = () => {
  // Reconectar após delay
  setTimeout(() => openChat(), 3000);
};

const sendMessage = (content: string) => {
  ws.send(JSON.stringify({ content }));
};
```

**RBAC:**
- Paciente: acessa apenas conversas do próprio `patient_id`
- Médico/secretária: acessa qualquer conversa da clínica

---

## ⏳ 🟡 Notificações

**Tela mobile:** `PerfilScreen` — item "Notificações" (sem destino atual)  
**Modelo necessário:** `Notification` (nova migration)  
**Entrega:** in-app (banco) + Expo Push via ARQ worker (requer `push_token` cadastrado ✅)

### `GET /users/{user_id}/notifications`

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `unread_only` | bool | false | Filtra apenas não lidas |
| `limit` | int | 20 | — |
| `offset` | int | 0 | — |

**Resposta 200:**
```json
{
  "total": 10,
  "unread": 3,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "type": "appointment_reminder",
      "title": "Consulta amanhã",
      "body": "Lembrete: consulta às 10h com Dra. Ana Lima.",
      "read": false,
      "created_at": "2024-03-14T18:00:00Z"
    }
  ]
}
```

Valores válidos para `type`: `appointment_reminder` · `clinic_announcement` · `vital_alert`

### `PATCH /notifications/{notification_id}/read`

**Resposta 200:**
```json
{ "read": true }
```

**Integração no app:**
```ts
// Badge de notificações (exibir contagem de não lidas):
const { data } = await api.get(`/users/${userId}/notifications?unread_only=true&limit=1`);
setUnreadCount(data.total);

// Ao abrir notificação:
await api.patch(`/notifications/${notification.id}/read`);
```

---

## ⏳ 🟡 Lembretes

**Tela mobile:** ação "Enviar Lembrete" no dashboard da secretária  
**Modelo necessário:** `Reminder` (nova migration)  
**Entrega:** enfileira job no ARQ worker que dispara push via Expo no horário agendado  
**RBAC:** `secretary`, `admin`

### `POST /patients/{patient_id}/reminders`

**Body:**
```json
{
  "type": "appointment",
  "message": "Lembrete: sua consulta é amanhã às 10h com Dra. Ana Lima.",
  "send_at": "2024-03-14T08:00:00Z"
}
```

Valores válidos para `type`: `appointment` · `exam` · `medication`

**Resposta 201:**
```json
{
  "id": "<uuid>",
  "patient_id": "<uuid>",
  "type": "appointment",
  "message": "Lembrete: sua consulta é amanhã às 10h com Dra. Ana Lima.",
  "send_at": "2024-03-14T08:00:00Z",
  "sent_at": null,
  "created_at": "2024-03-13T15:00:00Z"
}
```

> O campo `sent_at` é preenchido pelo worker ARQ quando o push é efetivamente enviado.

---

## ⏳ 🟡 Avisos — Detalhe e Leitura

Complementam os endpoints de listagem/criação já entregues na v1.

### `GET /clinics/{clinic_id}/announcements/{announcement_id}`

**Resposta 200:** objeto `AnnouncementResponse` completo (incluindo `full_description`)

**Erros:** `404` se não encontrado ou expirado

### `PATCH /clinics/{clinic_id}/announcements/{announcement_id}/read`

Marca o aviso como lido para o usuário autenticado. Cria registro na tabela pivot `user_announcement_reads`.

**Resposta 200:**
```json
{ "read": true, "read_at": "2024-03-15T09:30:00Z" }
```

**Integração no app:**
```ts
// Ao abrir detalhe do aviso:
const detail = await api.get(`/clinics/${clinicId}/announcements/${announcementId}`);
await api.patch(`/clinics/${clinicId}/announcements/${announcementId}/read`);
```

---

## ⏳ 🔵 Nomes de Bebê

**Tela mobile:** `NomesScreen` — stub atual  
**Modelos necessários:** `BabyName`, `PatientBabyNameFavorite` (nova migration + seed)

### `GET /baby-names`

**Query params:** `gender?` (`male` · `female` · `neutral`), `search?`, `limit`, `offset`

**Resposta 200:**
```json
{
  "total": 250,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "name": "Sofia",
      "gender": "female",
      "origin": "Grego",
      "meaning": "Sabedoria",
      "popularity_score": 92,
      "trend": "rising"
    }
  ]
}
```

Valores válidos para `trend`: `rising` · `stable` · `declining`

### `POST /patients/{patient_id}/baby-names/{name_id}/favorite`

**Resposta 201:** `{ "favorited": true }`

### `DELETE /patients/{patient_id}/baby-names/{name_id}/favorite`

**Resposta 204:** No Content

### `GET /patients/{patient_id}/baby-names/favorites`

**Resposta 200:** mesma estrutura de `GET /baby-names`, filtrado pelos favoritos da paciente

> **Nota para integração:** carregar a lista de favoritos junto com `GET /baby-names` e marcar localmente quais estão favoritados para evitar requisição por nome.

---

## ⏳ 🔵 Desenvolvimento Fetal

**Tela mobile:** `Feto3DScreen` — stub atual  
**Modelo necessário:** `FetalDevelopment` (migration + seed de 42 semanas)

### `GET /fetal-development/{week}`

Sem autenticação obrigatória. `week` deve ser entre 1 e 42.

**Resposta 200:**
```json
{
  "week": 24,
  "size_cm": 30.0,
  "weight_g": 600,
  "description": "O bebê já abre e fecha os olhos. Pode ouvir sua voz.",
  "highlights": [
    { "id": "lungs", "label": "Pulmões", "description": "Em desenvolvimento acelerado." },
    { "id": "hearing", "label": "Audição", "description": "Já responde a sons externos." }
  ],
  "image_url": null,
  "model_url": null
}
```

**Erros:** `404` se `week < 1` ou `week > 42`

**Integração no app:**
```ts
// Buscar dados da semana atual da paciente:
const { current_week } = usePatient();
const { data } = useQuery({
  queryKey: ['fetal-development', current_week],
  queryFn: () => api.get(`/fetal-development/${current_week}`),
  staleTime: Infinity, // Dados estáticos — nunca revalidar
});
```

---

## Resumo de status

| Feature | Status | Migration | Rotas |
|---|---|---|---|
| Exames laboratoriais | ✅ | `b1c2d3e4f5a6` | 3 |
| Medicamentos | ✅ | `b1c2d3e4f5a6` | 3 |
| Agendamento por paciente | ✅ | — | 1 |
| Relatório diário | ✅ | — | 1 |
| Onboarding flag | ✅ | `b1c2d3e4f5a6` | 1 |
| Push token | ✅ | `b1c2d3e4f5a6` | 1 |
| Chat WebSocket | ⏳ | pendente | 3 + WS |
| Notificações | ⏳ | pendente | 2 |
| Lembretes | ⏳ | pendente | 1 |
| Avisos (detalhe/lido) | ⏳ | pendente | 2 |
| Nomes de bebê | ⏳ | pendente + seed | 4 |
| Desenvolvimento fetal | ⏳ | pendente + seed | 1 |
