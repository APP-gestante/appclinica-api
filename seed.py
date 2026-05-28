import asyncio
import sys
from datetime import date, datetime, timedelta, time, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.core.security import get_password_hash
from app.models import (
    Clinic, User, Doctor, Patient, Secretary, 
    Appointment, Announcement, GlucoseReading, 
    BloodPressureReading, Contraction, Ultrasound, 
    Vaccine, LabTest, Medication, Message
)
from app.models.enums import (
    UserRole, RiskLevel, AppointmentStatus, 
    AppointmentType, PatientAppointmentStatus,
    AnnouncementCategory, VitalClassification,
    GlucoseMoment, TimeOfDay, UltrasoundType,
    FetalPresentation, VaccineStatus, LabTestType,
    LabTestStatus, MessageSenderType
)

async def seed_data():
    print("--- Iniciando semeadura COMPLETA de dados (Seed) ---")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Verificar ou criar a clínica principal
            clinic_stmt = select(Clinic).where(Clinic.name == "Clínica Gerar Vida")
            result = await session.execute(clinic_stmt)
            clinic = result.scalar_one_or_none()
            
            if not clinic:
                print("Criando clinica padrao...")
                clinic = Clinic(
                    name="Clínica Gerar Vida",
                    logo_url="https://murilin1711.github.io/lunna-cdn/branding/logos/lunna_logo.svg",
                    primary_color="#8DAA91",
                    secondary_color="#E5987D",
                    accent_color="#301B28",
                    address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
                    phone="(11) 3000-0000",
                    email="contato@gerarvida.com",
                    website="https://gerarvida.com"
                )
                session.add(clinic)
                await session.flush()
                print(f"Clinica criada com ID: {clinic.id}")
            else:
                print(f"Clinica ja existente (ID: {clinic.id})")

            # Hash da senha padrão para todos os usuários de teste
            default_password_hash = get_password_hash("senha_segura123")

            # 0. Criar Superadmin global
            sa_stmt = select(User).where(User.email == "superadmin@lunna.app")
            result = await session.execute(sa_stmt)
            superadmin_user = result.scalar_one_or_none()

            if not superadmin_user:
                print("Criando usuario Superadmin...")
                superadmin_user = User(
                    email="superadmin@lunna.app",
                    password_hash=get_password_hash("Lunna@2026"),
                    name="Lunna HQ",
                    role=UserRole.superadmin,
                    clinic_id=None,
                    is_active=True,
                    email_verified=True
                )
                session.add(superadmin_user)
            
            # 2. Usuário Administrador
            admin_stmt = select(User).where(User.email == "admin@gerarvida.com")
            result = await session.execute(admin_stmt)
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                print("Criando usuario Administrador...")
                admin_user = User(
                    email="admin@gerarvida.com",
                    password_hash=default_password_hash,
                    name="Admin Gerar Vida",
                    role=UserRole.admin,
                    clinic_id=clinic.id,
                    phone="(11) 91111-1111",
                    is_active=True,
                    email_verified=True
                )
                session.add(admin_user)

            # 3. Usuário Médico
            doctor_stmt = select(User).where(User.email == "doctor@gerarvida.com")
            result = await session.execute(doctor_stmt)
            doctor_user = result.scalar_one_or_none()
            
            if not doctor_user:
                print("Criando usuario Medico...")
                doctor_user = User(
                    email="doctor@gerarvida.com",
                    password_hash=default_password_hash,
                    name="Dr. Marcos Oliveira",
                    role=UserRole.doctor,
                    clinic_id=clinic.id,
                    phone="(11) 92222-2222",
                    is_active=True,
                    email_verified=True
                )
                session.add(doctor_user)
                await session.flush()
                
                doctor_profile = Doctor(
                    user_id=doctor_user.id,
                    specialty="Obstetrícia e Ginecologia",
                    crm="CRM-SP 123456",
                    bio="Médico obstetra especializado em gestações de alto risco e parto humanizado."
                )
                session.add(doctor_profile)

            # 4. Usuário Secretária
            sec_stmt = select(User).where(User.email == "secretary@gerarvida.com")
            result = await session.execute(sec_stmt)
            secretary_user = result.scalar_one_or_none()
            
            if not secretary_user:
                print("Criando usuario Secretaria...")
                secretary_user = User(
                    email="secretary@gerarvida.com",
                    password_hash=default_password_hash,
                    name="Ana Souza",
                    role=UserRole.secretary,
                    clinic_id=clinic.id,
                    phone="(11) 93333-3333",
                    is_active=True,
                    email_verified=True
                )
                session.add(secretary_user)
                await session.flush()
                
                secretary_profile = Secretary(
                    user_id=secretary_user.id,
                    position="Recepcionista Principal"
                )
                session.add(secretary_profile)

            # 5. Usuário Paciente (Gestante)
            patient_stmt = select(User).where(User.email == "patient@gerarvida.com")
            result = await session.execute(patient_stmt)
            patient_user = result.scalar_one_or_none()
            
            if not patient_user:
                print("Criando usuario Paciente (Gestante)...")
                patient_user = User(
                    email="patient@gerarvida.com",
                    password_hash=default_password_hash,
                    name="Maria da Silva",
                    role=UserRole.patient,
                    clinic_id=clinic.id,
                    phone="(11) 94444-4444",
                    is_active=True,
                    email_verified=True,
                    date_of_birth=date(1995, 8, 20)
                )
                session.add(patient_user)
                await session.flush()
                
                patient_profile = Patient(
                    user_id=patient_user.id,
                    doctor_id=doctor_user.id,
                    prontuario="PR-98765",
                    lmp_date=date.today() - timedelta(weeks=28),
                    edd=date.today() + timedelta(weeks=12),
                    current_week=28,
                    height_cm="165",
                    weight_initial_kg="62.5",
                    imc="22.9",
                    blood_type="O+",
                    risk_level=RiskLevel.low,
                    acompanhante="João da Silva (Marido)",
                    hospital="Hospital Maternidade Santa Joana",
                    number_of_fetuses=1,
                    cesarean_predicted=False
                )
                session.add(patient_profile)
                await session.flush()
            else:
                # Se já existe, pegamos o perfil para as relações abaixo
                patient_profile_stmt = select(Patient).where(Patient.user_id == patient_user.id)
                patient_profile = (await session.execute(patient_profile_stmt)).scalar_one()

            # --- DADOS FALTANTES (RELAÇÕES) ---

            # 6. Consultas (Appointments)
            print("Criando consultas...")
            # Consulta passada
            apt_past = Appointment(
                patient_id=patient_profile.id,
                doctor_id=doctor_user.id,
                clinic_id=clinic.id,
                date=date.today() - timedelta(days=7),
                time=time(14, 0),
                datetime=datetime.now(timezone.utc) - timedelta(days=7),
                status=AppointmentStatus.completed,
                type=AppointmentType.routine,
                notes="Consulta de rotina. Paciente bem."
            )
            # Consulta futura hoje
            apt_today = Appointment(
                patient_id=patient_profile.id,
                doctor_id=doctor_user.id,
                clinic_id=clinic.id,
                date=date.today(),
                time=time(16, 30),
                datetime=datetime.combine(date.today(), time(16, 30)).replace(tzinfo=timezone.utc),
                status=AppointmentStatus.confirmed,
                type=AppointmentType.routine
            )
            # Consulta futura próxima semana
            apt_future = Appointment(
                patient_id=patient_profile.id,
                doctor_id=doctor_user.id,
                clinic_id=clinic.id,
                date=date.today() + timedelta(days=14),
                time=time(9, 0),
                datetime=datetime.combine(date.today() + timedelta(days=14), time(9, 0)).replace(tzinfo=timezone.utc),
                status=AppointmentStatus.pending,
                type=AppointmentType.ultrasound
            )
            session.add_all([apt_past, apt_today, apt_future])

            # 7. Sinais Vitais (Vitals)
            print("Criando sinais vitais...")
            g1 = GlucoseReading(patient_id=patient_profile.id, value_mg_dl=Decimal("92.0"), moment=GlucoseMoment.fasting, classification=VitalClassification.Normal)
            g2 = GlucoseReading(patient_id=patient_profile.id, value_mg_dl=Decimal("145.0"), moment=GlucoseMoment.after_meal, classification=VitalClassification.Atenção)
            g2.created_at = datetime.now(timezone.utc) - timedelta(days=1)
            
            bp1 = BloodPressureReading(patient_id=patient_profile.id, systolic=110, diastolic=70, pulse_bpm=72, moment=TimeOfDay.morning, classification=VitalClassification.Normal)
            bp2 = BloodPressureReading(patient_id=patient_profile.id, systolic=135, diastolic=85, pulse_bpm=80, moment=TimeOfDay.afternoon, classification=VitalClassification.Atenção)
            bp2.created_at = datetime.now(timezone.utc) - timedelta(days=2)
            
            c1 = Contraction(patient_id=patient_profile.id, duration_seconds=35, interval_minutes=Decimal("10.5"), session_date=date.today())
            session.add_all([g1, g2, bp1, bp2, c1])

            # 8. Exames (Exams & Lab Tests)
            print("Criando exames e testes...")
            u1 = Ultrasound(
                patient_id=patient_profile.id, doctor_id=doctor_user.id,
                type=UltrasoundType.morphology, date=date.today() - timedelta(weeks=4),
                ig_weeks=24, presentation=FetalPresentation.cephalic,
                fetal_heart_rate=145, fetal_weight_g=Decimal("650.0")
            )
            v1 = Vaccine(patient_id=patient_profile.id, doctor_id=doctor_user.id, vaccine_type="dTpa", date=date.today() - timedelta(weeks=2), status=VaccineStatus.completed)
            lt1 = LabTest(
                patient_id=patient_profile.id, doctor_id=doctor_user.id,
                type=LabTestType.hemograma, name="Hemograma Completo",
                date=date.today() - timedelta(days=5), status=LabTestStatus.completed,
                result="Normal", reference_range="N/A"
            )
            session.add_all([u1, v1, lt1])

            # 9. Medicamentos (Medications)
            print("Criando medicamentos...")
            m1 = Medication(
                patient_id=patient_profile.id, doctor_id=doctor_user.id,
                name="Ácido Fólico", dosage="5mg", frequency="1x ao dia",
                start_date=date.today() - timedelta(weeks=20), active=True
            )
            m2 = Medication(
                patient_id=patient_profile.id, doctor_id=doctor_user.id,
                name="Sulfato Ferroso", dosage="40mg", frequency="1x ao dia",
                start_date=date.today() - timedelta(weeks=10), active=True
            )
            session.add_all([m1, m2])

            # 10. Avisos (Announcements)
            print("Criando avisos da clínica...")
            a1 = Announcement(
                clinic_id=clinic.id, category=AnnouncementCategory.clinica,
                title="Novo horário de atendimento",
                short_description="A partir de Junho teremos horários estendidos às terças.",
                full_description="Para melhor atender nossas gestantes, a Clínica Gerar Vida passará a atender até as 21h todas as terças-feiras.",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30)
            )
            a2 = Announcement(
                clinic_id=clinic.id, category=AnnouncementCategory.saude,
                title="Importância da hidratação",
                short_description="Dicas para manter o bem-estar durante o verão.",
                full_description="Beber pelo menos 2 litros de água por dia é fundamental para manter o líquido amniótico em níveis saudáveis.",
                expires_at=datetime.now(timezone.utc) + timedelta(days=60)
            )
            session.add_all([a1, a2])

            # 11. Mensagens (Messages)
            print("Criando mensagens de chat...")
            msg1 = Message(patient_id=patient_profile.id, sender_id=patient_user.id, sender_role=MessageSenderType.patient, content="Olá, Dr. Marcos! Gostaria de tirar uma dúvida sobre meu exame.")
            msg2 = Message(patient_id=patient_profile.id, sender_id=doctor_user.id, sender_role=MessageSenderType.doctor, content="Olá, Maria! Pode falar, como posso ajudar?")
            session.add_all([msg1, msg2])

            # Salvar tudo no banco de dados
            await session.commit()
            print("Semeadura COMPLETA concluida com sucesso!")
            
        except Exception as e:
            await session.rollback()
            print(f"Erro durante a semeadura: {e}")
            raise e

async def main():
    await seed_data()
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
