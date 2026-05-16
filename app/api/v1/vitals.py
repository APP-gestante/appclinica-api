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
async def get_contractions_stats(patient_id: UUID):
    """
    **Obter estatísticas agregadas sobre as contrações registradas.**

    *(Dados simulados/Mock)*
    Retorna métricas úteis baseadas no histórico recente da gestante, como duração média das contrações e frequência, para ajudar na tomada de decisão sobre ir à maternidade.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.

    ### 📤 Retornos esperados
    * **`200 OK`**: Métricas agregadas (total de contrações, duração média em segundos, etc.).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"patient_id": patient_id, "total_contractions": 12, "average_duration_seconds": 47}

@router.delete("/{patient_id}/contractions/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contraction_session(patient_id: UUID):
    """
    **Limpar o histórico de contrações da sessão do dia.**

    *(Dados simulados/Mock)*
    Permite descartar registros de um falso alarme de trabalho de parto ou iniciar uma nova contagem limpa.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.

    ### 📤 Retornos esperados
    * **`204 NO CONTENT`**: Descarte efetuado com sucesso. Sem corpo de retorno.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
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
async def get_glucose_stats(patient_id: UUID):
    """
    **Obter estatísticas consolidadas das leituras de glicose.**

    *(Dados simulados/Mock)*
    Retorna métricas como a média de açúcar no sangue, menor e maior valores lidos, e status consolidado para acompanhamento de diabetes gestacional.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Métricas de glicose (total de leituras, média, status).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"patient_id": patient_id, "total_readings": 15, "average": 92}

@router.get("/{patient_id}/glucose-readings/chart")
async def get_glucose_chart(patient_id: UUID, days: int = 30):
    """
    **Obter dados estruturados para a renderização de gráficos de glicose.**

    *(Dados simulados/Mock)*
    Retorna arrays otimizados para desenhar curvas de evolução glicêmica em elementos visuais (Canvas/SVG), incluindo limites de normalidade recomendados.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `days` *(int, opcional, query)*: Intervalo de dias para o gráfico (padrão: 30 dias).

    ### 📤 Retornos esperados
    * **`200 OK`**: Estrutura contendo a lista cronológica de valores e os limites (`normal_limit`, `hypertension_limit`).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"data": [], "normal_limit": 95, "hypertension_limit": 126}

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
async def get_blood_pressure_stats(patient_id: UUID):
    """
    **Obter estatísticas consolidadas e análise de risco para pressão arterial.**

    *(Dados simulados/Mock)*
    Retorna as médias sistólicas/diastólicas calculadas e uma sinalização de alerta para risco de hipertensão gestacional.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Resumo de dados de pressão (total de leituras, médias, classificação e nível de risco).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"patient_id": patient_id, "total_readings": 10, "average_systolic": 118, "average_diastolic": 78}

@router.get("/{patient_id}/blood-pressure/chart")
async def get_blood_pressure_chart(patient_id: UUID, days: int = 30):
    """
    **Obter dados estruturados para renderização de gráficos de pressão arterial.**

    *(Dados simulados/Mock)*
    Gera conjuntos de coordenadas ordenados cronologicamente contendo sistólica e diastólica para desenho de gráficos de linhas duplas.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📥 Parâmetros de Entrada
    * `patient_id` *(UUID, na URL)*: Identificador da paciente.
    * `days` *(int, opcional, query)*: Janela temporal em dias para o gráfico.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados para gráfico incluindo os limites clínicos recomendados (`normal_systolic`, `normal_diastolic`, `hypertension_limit`).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"data": [], "hypertension_limit": 140, "normal_systolic": 120, "normal_diastolic": 80}
