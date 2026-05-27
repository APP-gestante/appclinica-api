from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.crud import vitals as crud_vitals
from app.schemas.vitals import (
    ContractionCreate, ContractionResponse, ContractionListResponse,
    GlucoseReadingCreate, GlucoseReadingResponse, GlucoseListResponse,
    BloodPressureCreate, BloodPressureResponse, BloodPressureListResponse
)

router = APIRouter()

# --- Contractions ---
@router.post("/{patient_id}/contractions", response_model=ContractionResponse, status_code=status.HTTP_201_CREATED)
async def create_contraction(
    patient_id: UUID,
    obj_in: ContractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Registrar uma nova contração uterina de parto.**

    Este recurso permite à gestante cronometrar e registrar o momento, a duração em segundos e o intervalo em minutos entre as contrações. É fundamental para monitorar a evolução do trabalho de parto.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente gestante.
    * `duration_seconds` *(int, obrigatório, no corpo)*: Duração total da contração em segundos.
    * `interval_minutes` *(float, opcional, no corpo)*: Intervalo em minutos em relação à contração anterior.
    * `session_date` *(date, obrigatório, no corpo)*: Data de referência do monitoramento (`YYYY-MM-DD`).

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Registro de contração criado com sucesso. Retorna todos os dados persistidos e o ID do registro.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.create_contraction(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/contractions", response_model=ContractionListResponse)
async def list_contractions(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros a retornar"),
    offset: int = Query(0, ge=0, description="Ponto de partida para paginação"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Listar o histórico de contrações registradas da gestante.**

    Recupera as contrações registradas, útil para plotar cronogramas e acompanhar se os intervalos estão reduzindo de forma consistente (indicativo de trabalho de parto ativo).

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `limit` *(int, query)*: Quantidade de registros por página (máximo: 100).
    * `offset` *(int, query)*: Deslocamento para paginação.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada das contrações registradas.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    total, items = await crud_vitals.get_contractions(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/contractions/stats")
async def get_contractions_stats(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter estatísticas agregadas sobre as contrações registradas.**

    Retorna métricas calculadas sobre o histórico real da gestante: total de contrações, duração média e intervalo médio.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Métricas agregadas em tempo real.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.get_contractions_stats(db, patient_id=patient_id)

@router.delete("/{patient_id}/contractions/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contraction_session(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Limpar o histórico de contrações da sessão do dia.**

    Realiza soft-delete em todas as contrações registradas no dia corrente para a paciente especificada.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`204 NO CONTENT`**: Descarte efetuado com sucesso. Sem corpo de retorno.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    await crud_vitals.delete_contractions_session(db, patient_id=patient_id)
    return None

# --- Glucose ---
@router.post("/{patient_id}/glucose-readings", response_model=GlucoseReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_glucose(
    patient_id: UUID,
    obj_in: GlucoseReadingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Registrar uma nova leitura de glicemia (glicose).**

    Permite registrar os níveis de açúcar no sangue para acompanhamento e controle de diabetes gestacional. A leitura é automaticamente classificada em faixas de alerta.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `value_mg_dl` *(float, obrigatório, no corpo)*: Valor medido da glicose em mg/dL.
    * `moment` *(string, obrigatório, no corpo)*: Momento da medição (`fasting` (jejum), `after_meal` (pós-prandial), `random` (casual)).
    * `classification` *(string, obrigatório, no corpo)*: Classificação da leitura (`normal`, `attention` (atenção), `high` (alto)).
    * `notes` *(string, opcional, no corpo)*: Observações sobre alimentação recente ou dosagem de insulina.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Registro de glicemia cadastrado com sucesso.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.create_glucose(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/glucose-readings", response_model=GlucoseListResponse)
async def list_glucose_readings(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros a retornar"),
    offset: int = Query(0, ge=0, description="Ponto inicial da paginação"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Listar o histórico de medições de glicose da gestante.**

    Recupera as leituras anteriores para monitoramento sistemático dos níveis de açúcar ao longo do tempo.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `limit` *(int, query)*: Quantidade máxima de registros.
    * `offset` *(int, query)*: Ponto inicial da paginação.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista contendo o histórico paginado de glicose.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    total, items = await crud_vitals.get_glucose_readings(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/glucose-readings/stats")
async def get_glucose_stats(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter estatísticas consolidadas das leituras de glicose.**

    Retorna métricas calculadas sobre os dados reais: total de leituras, média, mínimo, máximo e última leitura.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Métricas de glicose em tempo real.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.get_glucose_stats(db, patient_id=patient_id)

@router.get("/{patient_id}/glucose-readings/chart")
async def get_glucose_chart(
    patient_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Janela temporal em dias para o gráfico"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter dados estruturados para renderização de gráficos de glicose.**

    Retorna série temporal real das leituras de glicose no intervalo especificado.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Série temporal com limites clínicos (`normal_limit`, `hypertension_limit`).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.get_glucose_chart(db, patient_id=patient_id, days=days)

# --- Blood Pressure ---
@router.post("/{patient_id}/blood-pressure", response_model=BloodPressureResponse, status_code=status.HTTP_201_CREATED)
async def create_blood_pressure(
    patient_id: UUID,
    obj_in: BloodPressureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Registrar uma nova leitura de pressão arterial.**

    Registra as pressões sistólica (máxima) e diastólica (mínima), bem como a frequência cardíaca. Vital para prevenir e detectar quadros de pré-eclâmpsia.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `systolic` *(int, obrigatório, no corpo)*: Pressão sistólica em mmHg (ex: 120).
    * `diastolic` *(int, obrigatório, no corpo)*: Pressão diastólica em mmHg (ex: 80).
    * `pulse_bpm` *(int, opcional, no corpo)*: Frequência cardíaca medida em batimentos por minuto.
    * `moment` *(string, obrigatório, no corpo)*: Período do dia da medição (`morning` (manhã), `afternoon` (tarde), `evening` (fim de tarde), `night` (noite)).
    * `classification` *(string, obrigatório, no corpo)*: Classificação da pressão (`normal`, `attention` (atenção), `high` (alto)).

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Leitura de pressão arterial registrada com sucesso.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.create_blood_pressure(db, patient_id=patient_id, obj_in=obj_in)

@router.get("/{patient_id}/blood-pressure", response_model=BloodPressureListResponse)
async def list_blood_pressure_readings(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros a retornar"),
    offset: int = Query(0, ge=0, description="Ponto de partida para a paginação"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Listar o histórico de registros de pressão arterial.**

    Obtém a lista paginada de leituras de pressão arterial registradas pela gestante.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `limit` *(int, query)*: Registros por página.
    * `offset` *(int, query)*: Deslocamento de paginação.

    ### 📤 Retornos esperados
    * **`200 OK`**: Lista paginada das leituras.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    total, items = await crud_vitals.get_blood_pressure_readings(db, patient_id=patient_id, skip=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "data": items}

@router.get("/{patient_id}/blood-pressure/stats")
async def get_blood_pressure_stats(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter estatísticas consolidadas de pressão arterial.**

    Retorna médias sistólicas/diastólicas calculadas e última leitura registrada em tempo real.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Resumo calculado sobre dados reais.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.get_blood_pressure_stats(db, patient_id=patient_id)

@router.get("/{patient_id}/blood-pressure/chart")
async def get_blood_pressure_chart(
    patient_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Janela temporal em dias para o gráfico"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Obter dados para gráfico de linhas duplas de pressão arterial.**

    Retorna série temporal real de sistólica e diastólica com limites clínicos.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Série temporal com `hypertension_limit`, `normal_systolic` e `normal_diastolic`.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return await crud_vitals.get_blood_pressure_chart(db, patient_id=patient_id, days=days)
