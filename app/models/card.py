from sqlalchemy import Column, ForeignKey, String, Text, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class DoctorCardSection(BaseModel):
    """Template do médico — define estrutura, ordem e visibilidade do cartão."""
    __tablename__ = 'doctor_card_sections'

    doctor_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(100), nullable=False)
    section_type = Column(String(20), nullable=False)   # 'builtin' | 'text' | 'fields'
    builtin_key = Column(String(50), nullable=True)     # 'dados_gestacionais' | 'evolucao' | 'exames' | 'vacinas' | 'medicamentos' | 'anamnese'
    position = Column(Integer, nullable=False, default=0)
    visible = Column(Boolean, nullable=False, default=True)

    doctor = relationship("User")
    entries = relationship("PatientCardEntry", back_populates="section", cascade="all, delete-orphan")
    field_values = relationship("PatientCardFieldValue", back_populates="section", cascade="all, delete-orphan")


class PatientCardEntry(BaseModel):
    """Conteúdo de texto de uma seção por paciente."""
    __tablename__ = 'patient_card_entries'
    __table_args__ = (UniqueConstraint('patient_id', 'section_id'),)

    patient_id = Column(ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    section_id = Column(ForeignKey('doctor_card_sections.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=True)

    patient = relationship("Patient")
    section = relationship("DoctorCardSection", back_populates="entries")


class PatientCardFieldValue(BaseModel):
    """Pares label+valor de seções do tipo 'fields' por paciente."""
    __tablename__ = 'patient_card_field_values'

    patient_id = Column(ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    section_id = Column(ForeignKey('doctor_card_sections.id', ondelete='CASCADE'), nullable=False)
    label = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)

    patient = relationship("Patient")
    section = relationship("DoctorCardSection", back_populates="field_values")
