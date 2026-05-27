from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.fetal_development import FetalDevelopment
from app.schemas.fetal_development import FetalDevelopmentResponse

router = APIRouter()


@router.get("/fetal-development/{week}", response_model=FetalDevelopmentResponse)
async def get_fetal_development(
    week: int,
    db: AsyncSession = Depends(get_db),
):
    """
    **Obter informações de desenvolvimento fetal para uma semana gestacional específica.**

    Recurso público — não requer autenticação. Retorna tamanho, peso, descrição e marcos de desenvolvimento.

    ### 📤 Retornos esperados
    * **`200 OK`**: Dados do desenvolvimento fetal na semana solicitada.
    * **`404 NOT FOUND`**: Semana inválida (< 1 ou > 42) ou não encontrada no banco.
    """
    if week < 1 or week > 42:
        raise HTTPException(status_code=404, detail="Week must be between 1 and 42")

    result = await db.execute(
        select(FetalDevelopment).where(FetalDevelopment.week == week)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Fetal development data not found for this week")

    return record
