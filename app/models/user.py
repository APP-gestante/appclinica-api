from sqlalchemy import Column, String, ForeignKey, Boolean, Date, Enum as SQLEnum, Text, SmallInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import UserRole, RiskLevel

class User(BaseModel):
    __tablename__ = 'users'
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.patient)
    clinic_id = Column(ForeignKey('clinics.id', ondelete='RESTRICT'), nullable=False)
    avatar_url = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    push_token = Column(String(512), nullable=True)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    
    # Relações
    clinic = relationship("Clinic", back_populates="users")
    patient_profile = relationship("Patient", foreign_keys="[Patient.user_id]", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    secretary_profile = relationship("Secretary", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Patient(BaseModel):
    __tablename__ = 'patients'
    
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    doctor_id = Column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    
    prontuario = Column(String(20), unique=True, nullable=False)
    lmp_date = Column(Date, nullable=False)
    edd = Column(Date, nullable=False)
    current_week = Column(SmallInteger, nullable=True)
    
    height_cm = Column(String(10), nullable=True)
    weight_initial_kg = Column(String(10), nullable=True)
    imc = Column(String(10), nullable=True)
    blood_type = Column(String(5), nullable=True)
    
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.low)
    
    acompanhante = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)
    
    number_of_fetuses = Column(SmallInteger, default=1)
    parity = Column(String(10), nullable=True)
    cesarean_predicted = Column(Boolean, default=False)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="patient_profile")
    doctor = relationship("User", foreign_keys=[doctor_id])


class Doctor(BaseModel):
    __tablename__ = 'doctors'
    
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    specialty = Column(String(100), nullable=False)
    crm = Column(String(20), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="doctor_profile")


class Secretary(BaseModel):
    __tablename__ = 'secretaries'
    
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    position = Column(String(100), nullable=True)
    
    user = relationship("User", back_populates="secretary_profile")
