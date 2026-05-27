from sqlalchemy import Column, Text, SmallInteger, Numeric
from sqlalchemy.dialects.postgresql import JSON
from app.models.base import BaseModel


class FetalDevelopment(BaseModel):
    __tablename__ = "fetal_development"

    week = Column(SmallInteger, unique=True, nullable=False, index=True)
    size_cm = Column(Numeric(5, 2), nullable=True)
    weight_g = Column(Numeric(7, 2), nullable=True)
    description = Column(Text, nullable=False)
    highlights = Column(JSON, nullable=True)
    image_url = Column(Text, nullable=True)
    model_url = Column(Text, nullable=True)
