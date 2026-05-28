import asyncio
import sys
from datetime import date
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.core.security import get_password_hash
from app.models import Clinic, User, Doctor, Patient, Secretary
from app.models.enums import UserRole, RiskLevel

async def seed_data():
    print("--- Iniciando semeadura de dados de teste (Seed) ---")
    
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
                    logo_url="https://lunnaclinica.com/logo.png",
                    primary_color="#8DAA91",
                    secondary_color="#E5987D",
                    accent_color="#4A5E51",
                    address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
                    phone="(11) 3000-0000",
                    email="contato@gerarvida.com",
                    website="https://gerarvida.com"
                )
                session.add(clinic)
                await session.flush()  # Garante a geração do ID da clínica
                print(f"Clinica criada com ID: {clinic.id}")
            else:
                print(f"Clinica ja existente (ID: {clinic.id})")

            # Hash da senha padrão para todos os usuários de teste
            default_password_hash = get_password_hash("senha_segura123")

            # 0. Criar Superadmin global (sem clinic_id)
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
                print("Superadmin criado.")
            else:
                print("Superadmin ja cadastrado.")

            # 2. Criar Usuário Administrador
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
                print("Administrador criado.")
            else:
                print("Administrador ja cadastrado.")

            # 3. Criar Usuário Médico
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
                await session.flush()  # Garante ID do usuário médico
                
                print("Criando perfil detalhado de Medico...")
                doctor_profile = Doctor(
                    user_id=doctor_user.id,
                    specialty="Obstetrícia e Ginecologia",
                    crm="CRM-SP 123456",
                    bio="Médico obstetra especializado em gestações de alto risco e parto humanizado."
                )
                session.add(doctor_profile)
                print("Medico e seu perfil detalhado foram criados.")
            else:
                print("Medico ja cadastrado.")

            # 4. Criar Usuário Secretária
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
                
                print("Criando perfil detalhado de Secretaria...")
                secretary_profile = Secretary(
                    user_id=secretary_user.id,
                    position="Recepcionista Principal"
                )
                session.add(secretary_profile)
                print("Secretaria e seu perfil detalhado foram criados.")
            else:
                print("Secretaria ja cadastrada.")

            # 5. Criar Usuário Paciente (Gestante)
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
                
                print("Criando perfil detalhado de Paciente gestante...")
                patient_profile = Patient(
                    user_id=patient_user.id,
                    doctor_id=doctor_user.id,  # Vinculado ao Dr. Marcos
                    prontuario="PR-98765",
                    lmp_date=date(2023, 11, 1),  # Data da Última Menstruação
                    edd=date(2024, 8, 7),        # Data Provável do Parto
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
                print("Paciente gestante e seu perfil detalhado foram criados.")
            else:
                print("Paciente gestante ja cadastrada.")

            # Salvar tudo no banco de dados
            await session.commit()
            print("Semeadura concluida com sucesso!")
            
        except Exception as e:
            await session.rollback()
            print(f"Erro durante a semeadura: {e}")
            raise e

async def main():
    await seed_data()
    # Fecha a conexão do pool de banco de dados
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
