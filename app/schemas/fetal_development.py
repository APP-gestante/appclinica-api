from typing import Optional, Any, List
from app.schemas.base import BaseEntitySchema
from app.models.enums import BabyNameGender


class FetalDevelopmentResponse(BaseEntitySchema):
    week: int
    size_cm: Optional[float] = None
    weight_g: Optional[float] = None
    description: str
    highlights: Optional[Any] = None
    image_url: Optional[str] = None
    model_url: Optional[str] = None
