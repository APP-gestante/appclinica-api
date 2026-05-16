import pytest
from httpx import AsyncClient
from app.core.security import get_password_hash
from app.models.user import User, Clinic
from app.models.enums import UserRole
import uuid

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Gerar Vida API"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session):
    # Setup - criar clínica e usuário fake
    clinic = Clinic(id=uuid.uuid4(), name="Clinica Teste")
    db_session.add(clinic)
    
    user = User(
        id=uuid.uuid4(),
        email="test@clinic.com",
        password_hash=get_password_hash("password123"),
        name="Teste User",
        role=UserRole.doctor,
        clinic_id=clinic.id
    )
    db_session.add(user)
    await db_session.commit()
    
    # Executar login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@clinic.com", "password": "password123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@clinic.com"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@clinic.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
