from sqlalchemy import Column, ForeignKey, SmallInteger, Numeric, Boolean, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import FetalPresentation


class AppointmentEvolution(BaseModel):
    __tablename__ = 'appointment_evolutions'

    appointment_id = Column(
        ForeignKey('appointments.id', ondelete='CASCADE'),
        unique=True, nullable=False,
    )
    patient_id = Column(
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
    )

    weight_kg = Column(Numeric(5, 2), nullable=True)
    fundal_height_cm = Column(Numeric(4, 1), nullable=True)
    fetal_heart_rate = Column(SmallInteger, nullable=True)
    presentation = Column(SQLEnum(FetalPresentation, create_type=False), nullable=True)
    fetal_movements = Column(Boolean, nullable=True)
    edema = Column(String(5), nullable=True)   # 'none' | '+' | '++' | '+++'
    bp_systolic = Column(SmallInteger, nullable=True)
    bp_diastolic = Column(SmallInteger, nullable=True)
    clinical_notes = Column(Text, nullable=True)

    appointment = relationship("Appointment")
    patient = relationship("Patient")
