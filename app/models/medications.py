from sqlalchemy import Column, ForeignKey, Date, String, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Medication(BaseModel):
    __tablename__ = "medications"

    patient_id = Column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    instructions = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
