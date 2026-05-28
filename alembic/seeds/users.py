"""
Seed: users
Run: python alembic/seeds/users.py
"""
import asyncio
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.core.security import get_password_hash
from app.models import Clinic, User, Doctor, Patient, Secretary
from app.models.enums import UserRole, RiskLevel

async def run():
    async with AsyncSessionLocal() as session:
        clinic_stmt = select(Clinic).where(Clinic.name == "Clínica Gerar Vida")
        result = await session.execute(clinic_stmt)
        clinic = result.scalar_one_or_none()

        if not clinic:
            clinic = Clinic(
                name="Clínica Gerar Vida",
                logo_url="https://lunnaclinica.com/logo.png",
                primary_color="#8DAA91",
                secondary_color="#E5987D",
                accent_color="#4A5E51",
                address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
                phone="(11) 3000-0000",
                email="contato@gerarvida.com",
                website="https://gerarvida.com",
            )
            session.add(clinic)
            await session.flush()
            print(f"Clinica criada: {clinic.name} (ID: {clinic.id})")
        else:
            print(f"Clinica existente: {clinic.name} (ID: {clinic.id})")

        default_password_hash = get_password_hash("senha_segura123")

        users = [
            {
                "email": "superadmin@lunna.app",
                "name": "Lunna Superadmin",
                "role": UserRole.superadmin,
                "clinic_id": None,
                "password_hash": get_password_hash("Lunna@2026"),
                "is_active": True,
                "email_verified": True,
            },
            {
                "email": "admin@gerarvida.com",
                "name": "Admin Gerar Vida",
                "role": UserRole.admin,
                "clinic_id": clinic.id,
                "password_hash": default_password_hash,
                "phone": "(11) 91111-1111",
                "is_active": True,
                "email_verified": True,
            },
            {
                "email": "doctor@gerarvida.com",
                "name": "Dr. Marcos Oliveira",
                "role": UserRole.doctor,
                "clinic_id": clinic.id,
                "password_hash": default_password_hash,
                "phone": "(11) 92222-2222",
                "is_active": True,
                "email_verified": True,
            },
            {
                "email": "secretary@gerarvida.com",
                "name": "Ana Souza",
                "role": UserRole.secretary,
                "clinic_id": clinic.id,
                "password_hash": default_password_hash,
                "phone": "(11) 93333-3333",
                "is_active": True,
                "email_verified": True,
            },
            {
                "email": "patient@gerarvida.com",
                "name": "Maria da Silva",
                "role": UserRole.patient,
                "clinic_id": clinic.id,
                "password_hash": default_password_hash,
                "phone": "(11) 94444-4444",
                "is_active": True,
                "email_verified": True,
                "date_of_birth": date(1995, 8, 20),
            },
        ]

        created = 0
        user_map = {}

        for user_data in users:
            user_stmt = select(User).where(User.email == user_data["email"])
            result = await session.execute(user_stmt)
            user = result.scalar_one_or_none()

            if user:
                print(f"Usuário já existe: {user.email} ({user.role})")
                user_map[user_data["email"]] = user
                continue

            user = User(**{k: v for k, v in user_data.items() if v is not None})
            session.add(user)
            await session.flush()
            user_map[user.email] = user
            created += 1
            print(f"Criado usuário: {user.email} ({user.role})")

            if user.role == UserRole.doctor:
                doctor_profile = Doctor(
                    user_id=user.id,
                    specialty="Obstetrícia e Ginecologia",
                    crm="CRM-SP 123456",
                    bio="Médico obstetra especializado em gestações de alto risco e parto humanizado.",
                )
                session.add(doctor_profile)
                print("  Perfil de doctor criado.")

            if user.role == UserRole.secretary:
                secretary_profile = Secretary(
                    user_id=user.id,
                    position="Recepcionista Principal",
                )
                session.add(secretary_profile)
                print("  Perfil de secretary criado.")

            if user.role == UserRole.patient:
                doctor_user = user_map.get("doctor@gerarvida.com")
                if not doctor_user:
                    doctor_select = select(User).where(User.email == "doctor@gerarvida.com")
                    doctor_result = await session.execute(doctor_select)
                    doctor_user = doctor_result.scalar_one_or_none()

                doctor_id = doctor_user.id if doctor_user else None

                patient_profile = Patient(
                    user_id=user.id,
                    doctor_id=doctor_id or user.id,
                    prontuario="PR-98765",
                    lmp_date=date(2023, 11, 1),
                    edd=date(2024, 8, 7),
                    current_week=28,
                    height_cm="165",
                    weight_initial_kg="62.5",
                    imc="22.9",
                    blood_type="O+",
                    risk_level=RiskLevel.low,
                    acompanhante="João da Silva (Marido)",
                    hospital="Hospital Maternidade Santa Joana",
                    number_of_fetuses=1,
                    cesarean_predicted=False,
                )
                session.add(patient_profile)
                print("  Perfil de patient criado.")

        await session.commit()
        print(f"Seed concluído. Usuários criados: {created}")


async def main():
    await run()
    await engine.dispose()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
