from sqlalchemy import Column, String, Text, SmallInteger, Enum as SQLEnum, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.enums import BabyNameGender, NameTrend


class BabyName(BaseModel):
    __tablename__ = "baby_names"

    name = Column(String(100), nullable=False, index=True)
    gender = Column(SQLEnum(BabyNameGender), nullable=False)
    origin = Column(String(100), nullable=True)
    meaning = Column(Text, nullable=True)
    popularity_score = Column(SmallInteger, nullable=True)
    trend = Column(SQLEnum(NameTrend), nullable=True)


class PatientBabyNameFavorite(BaseModel):
    __tablename__ = "patient_baby_name_favorites"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    baby_name_id = Column(UUID(as_uuid=True), ForeignKey("baby_names.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("patient_id", "baby_name_id", name="uq_patient_baby_name"),
    )
