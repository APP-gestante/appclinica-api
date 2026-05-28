from typing import Optional, List
from uuid import UUID
from app.schemas.base import CoreModel, BaseEntitySchema
from app.models.enums import BabyNameGender, NameTrend


class BabyNameResponse(BaseEntitySchema):
    name: str
    gender: BabyNameGender
    origin: Optional[str] = None
    meaning: Optional[str] = None
    popularity_score: Optional[int] = None
    trend: Optional[NameTrend] = None
    is_favorite: bool = False


class BabyNameListResponse(CoreModel):
    total: int
    limit: int
    offset: int
    data: List[BabyNameResponse]


class FavoriteResponse(CoreModel):
    patient_id: UUID
    baby_name_id: UUID
    message: str = "Adicionado aos favoritos"
