from sqlalchemy import Column, ForeignKey, Date, String, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import LabTestType, LabTestStatus


class LabTest(BaseModel):
    __tablename__ = "lab_tests"

    patient_id = Column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    type = Column(SQLEnum(LabTestType), nullable=False)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    result = Column(Text, nullable=True)
    reference_range = Column(String(255), nullable=True)
    status = Column(SQLEnum(LabTestStatus), default=LabTestStatus.pending, nullable=False)
    file_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
