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
| Notificações | ✅ | `GET /users/{id}/notifications`, `PATCH /notifications/{id}/read` |
| Lembretes | ✅ | `POST /patients/{id}/reminders` |
| Nomes de bebê | ✅ | 4 rotas + seed 203 nomes |
| Desenvolvimento fetal | ✅ | `GET /fetal-development/{week}` + seed 42 semanas |
| Chat / Mensagens | ✅ | `GET/POST /patients/{id}/messages`, `PATCH .../read` + WebSocket |
| Avisos — detalhe + lido | ✅ | `GET/PATCH /clinics/{id}/announcements/{id}[/read]` |

**Todas as 22 rotas da v2 estão implementadas.**

---

## Setup completo (todas as fases)

```bash
# 1. Aplicar todas as migrations em ordem
alembic upgrade head

# 2. Popular dados estáticos (executar uma única vez)
python alembic/seeds/baby_names.py       # 203 nomes de bebê
python alembic/seeds/fetal_development.py  # 42 semanas gestacionais

# 3. Iniciar worker ARQ (notificações + lembretes)
arq app.worker.WorkerSettings
```

### Cadeia de migrations

| ID | Descrição |
|---|---|
| `a1b2c3d4e5f6` | `announcements` |
| `b1c2d3e4f5a6` | `lab_tests`, `medications`, `push_token`, `onboarding_completed` |
| `c1d2e3f4a5b6` | `notifications`, `reminders` |
| `d1e2f3a4b5c6` | `baby_names`, `patient_baby_name_favorites`, `fetal_development` |
| `e1f2a3b4c5d6` | `messages`, `user_announcement_reads` |

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

## ✅ Notificações

**Tela mobile:** `PerfilScreen` — item "Notificações"  
**Migration:** `c1d2e3f4a5b6`  
**Entrega:** in-app (banco) + Expo Push via worker ARQ (requer `push_token` cadastrado)

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
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "user_id": "<uuid>",
      "type": "appointment_reminder",
      "title": "Consulta amanhã",
      "body": "Lembrete: consulta às 10h com Dra. Ana Lima.",
      "read": false,
      "data": null,
      "created_at": "2024-03-14T18:00:00Z",
      "updated_at": "2024-03-14T18:00:00Z"
    }
  ]
}
```

Valores válidos para `type`: `appointment_reminder` · `clinic_announcement` · `vital_alert`

### `PATCH /notifications/{notification_id}/read`

**Resposta 200:** objeto `NotificationResponse` com `read: true`

**Integração no app:**
```ts
// Badge de notificações não lidas:
const { data } = await api.get(`/users/${userId}/notifications?unread_only=true&limit=1`);
setUnreadCount(data.total);

// Ao abrir uma notificação:
await api.patch(`/notifications/${notification.id}/read`);
```

---

## ✅ Lembretes

**Tela mobile:** ação "Enviar Lembrete" no dashboard da secretária  
**Migration:** `c1d2e3f4a5b6`  
**Entrega:** job ARQ com `_defer_until=send_at` — dispara push Expo no horário agendado  
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
  "created_by": "<uuid>",
  "type": "appointment",
  "message": "Lembrete: sua consulta é amanhã às 10h com Dra. Ana Lima.",
  "send_at": "2024-03-14T08:00:00Z",
  "sent_at": null,
  "created_at": "2024-03-13T15:00:00Z",
  "updated_at": "2024-03-13T15:00:00Z"
}
```

> O campo `sent_at` é preenchido pelo worker ARQ quando o push é efetivamente enviado.  
> O worker deve estar rodando: `arq app.worker.WorkerSettings`

---

## ✅ Nomes de Bebê

**Tela mobile:** `NomesScreen`  
**Migration:** `d1e2f3a4b5c6`  
**Seed:** `python alembic/seeds/baby_names.py` — 203 nomes (femininos, masculinos, neutros)

### `GET /baby-names`

**Query params:** `gender?` (`male` · `female` · `neutral`), `search?`, `limit`, `offset`

**Resposta 200:**
```json
{
  "total": 203,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "<uuid>",
      "name": "Sofia",
      "gender": "female",
      "origin": "Grego",
      "meaning": "sabedoria",
      "popularity_score": 95,
      "trend": "rising",
      "is_favorite": false,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

> O campo `is_favorite` é preenchido automaticamente para usuários com role `patient`.

Valores válidos para `gender`: `male` · `female` · `neutral`  
Valores válidos para `trend`: `rising` · `stable` · `declining`

### `POST /patients/{patient_id}/baby-names/{name_id}/favorite`

**Resposta 201:**
```json
{
  "patient_id": "<uuid>",
  "baby_name_id": "<uuid>",
  "message": "Adicionado aos favoritos"
}
```

**Erros:** `409 CONFLICT` se já estiver nos favoritos

### `DELETE /patients/{patient_id}/baby-names/{name_id}/favorite`

**Resposta 204:** No Content  
**Erros:** `404` se o favorito não existir

### `GET /patients/{patient_id}/baby-names/favorites`

**Resposta 200:** mesma estrutura de `GET /baby-names`, com `is_favorite: true` em todos os itens

**Integração no app:**
```ts
// Carregar lista com favoritos já marcados (para usuário patient):
const { data } = await api.get('/baby-names?limit=50');
// data.data[n].is_favorite já vem preenchido pelo backend

// Favoritar um nome:
await api.post(`/patients/${patientId}/baby-names/${nameId}/favorite`);

// Desfavoritar:
await api.delete(`/patients/${patientId}/baby-names/${nameId}/favorite`);
```

---

## ✅ Desenvolvimento Fetal

**Tela mobile:** `Feto3DScreen`  
**Migration:** `d1e2f3a4b5c6`  
**Seed:** `python alembic/seeds/fetal_development.py` — semanas 1 a 42  
**Auth:** não requer autenticação

### `GET /fetal-development/{week}`

`week` deve ser inteiro entre 1 e 42.

**Resposta 200:**
```json
{
  "id": "<uuid>",
  "week": 24,
  "size_cm": 30.0,
  "weight_g": 600.0,
  "description": "Os olhos se abrem pela primeira vez! O bebê responde à luz.",
  "highlights": [
    { "id": "1", "label": "Olhos abertos", "description": "Pálpebras se abrem e fecham." },
    { "id": "2", "label": "Resposta à luz", "description": "Bebê reage a lanterna sobre o abdômen." }
  ],
  "image_url": null,
  "model_url": null,
  "created_at": "...",
  "updated_at": "..."
}
```

**Erros:** `404` se `week < 1`, `week > 42` ou semana não encontrada no banco

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

## ✅ Chat / Mensagens — WebSocket + HTTP

**Tela mobile:** `ChatScreen`  
**Migration:** `e1f2a3b4c5d6`  
**Arquitetura:** WebSocket nativo FastAPI + Redis Pub/Sub por conexão

### `GET /patients/{patient_id}/messages`

Lista histórico paginado. Use `before_id` para carregar mensagens mais antigas (cursor reverso).

**Query params:**
| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `limit` | int | 30 | — |
| `offset` | int | 0 | — |
| `before_id` | uuid | — | Retorna mensagens anteriores a este ID (cursor) |

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
      "content": "Seus exames estão ótimos!",
      "read": false,
      "created_at": "2024-03-15T10:00:00Z",
      "updated_at": "2024-03-15T10:00:00Z"
    }
  ]
}
```

Valores válidos para `sender_role`: `patient` · `doctor` · `secretary` · `system`

### `POST /patients/{patient_id}/messages`

Envia mensagem via HTTP (fallback offline ou notificação sem WS ativo). Também publica no canal Redis.

**Body:**
```json
{ "content": "Dra, tenho uma dúvida sobre a dieta." }
```

**Resposta 201:** objeto `MessageResponse`

### `PATCH /patients/{patient_id}/messages/read`

Marca todas as mensagens não lidas da conversa como lidas.

**Resposta 204:** No Content

---

### WebSocket — Tempo real

#### `WS /patients/{patient_id}/ws/chat?token=<access_token>`

> O header `Authorization` não é suportado em conexões WebSocket. O token JWT deve ir no query param `token`.

**Protocolo:**

1. App abre conexão: `ws://<host>/api/v1/patients/<uuid>/ws/chat?token=<jwt>`
2. Servidor valida JWT, registra conexão no `ConnectionManager` e subscreve no canal Redis `chat:<patient_id>`
3. App envia mensagem:
```json
{ "content": "Olá Dra., tudo bem?" }
```
4. Servidor persiste no banco → publica no Redis → todos os clientes conectados ao mesmo `patient_id` recebem em tempo real
5. Todos os clientes recebem (formato `MessageResponse`):
```json
{
  "id": "<uuid>",
  "patient_id": "<uuid>",
  "sender_id": "<uuid>",
  "sender_role": "patient",
  "content": "Olá Dra., tudo bem?",
  "read": false,
  "created_at": "2024-03-15T10:05:00Z",
  "updated_at": "2024-03-15T10:05:00Z"
}
```
6. App deve reconectar automaticamente ao perder conexão (back-off exponencial recomendado)

**Código de erro WS:** `4001` = token inválido ou expirado

**Integração no app:**
```ts
const ws = new WebSocket(
  `${WS_BASE_URL}/patients/${patientId}/ws/chat?token=${accessToken}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  setMessages(prev => [message, ...prev]);
};

ws.onclose = (event) => {
  if (event.code === 4001) return; // Token inválido — não reconectar
  setTimeout(() => openChat(), 3000); // Reconectar após 3s
};

const sendMessage = (content: string) => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ content }));
  } else {
    // Fallback: enviar via HTTP
    api.post(`/patients/${patientId}/messages`, { content });
  }
};
```

**Teste via CLI:**
```bash
wscat -c "ws://localhost:8000/api/v1/patients/<uuid>/ws/chat?token=<jwt>"
# Enviar: {"content":"Olá Dra."}
```

---

## ✅ Avisos — Detalhe e Leitura

**Migration:** `e1f2a3b4c5d6` (tabela `user_announcement_reads`)  
Complementam os endpoints de listagem/criação já entregues na v1.

### `GET /clinics/{clinic_id}/announcements/{announcement_id}`

**Resposta 200:** objeto `AnnouncementResponse` completo (incluindo `full_description` e campo `is_new`)

**Erros:** `404` se não encontrado

### `PATCH /clinics/{clinic_id}/announcements/{announcement_id}/read`

Marca o aviso como lido para o usuário autenticado. Cria registro em `user_announcement_reads`.  
Idempotente — chamadas repetidas não duplicam.

**Resposta 204:** No Content

**Integração no app:**
```ts
// Ao abrir o detalhe do aviso:
const detail = await api.get(`/clinics/${clinicId}/announcements/${announcementId}`);
await api.patch(`/clinics/${clinicId}/announcements/${announcementId}/read`);
```

---

## Resumo de status

| Feature | Status | Migration | Worker | Seed | Rotas |
|---|---|---|---|---|---|
| Exames laboratoriais | ✅ | `b1c2d3e4f5a6` | — | — | 3 |
| Medicamentos | ✅ | `b1c2d3e4f5a6` | — | — | 3 |
| Agendamento por paciente | ✅ | — | — | — | 1 |
| Relatório diário | ✅ | — | — | — | 1 |
| Onboarding flag | ✅ | `b1c2d3e4f5a6` | — | — | 1 |
| Push token | ✅ | `b1c2d3e4f5a6` | — | — | 1 |
| Notificações | ✅ | `c1d2e3f4a5b6` | `send_push_notification` | — | 2 |
| Lembretes | ✅ | `c1d2e3f4a5b6` | `send_reminder` | — | 1 |
| Nomes de bebê | ✅ | `d1e2f3a4b5c6` | — | ✅ 203 nomes | 4 |
| Desenvolvimento fetal | ✅ | `d1e2f3a4b5c6` | — | ✅ 42 semanas | 1 |
| Chat WebSocket | ✅ | `e1f2a3b4c5d6` | — | — | 3 + WS |
| Avisos (detalhe/lido) | ✅ | `e1f2a3b4c5d6` | — | — | 2 |
| **Total** | **12 / 12** | | | | **23 rotas** |
