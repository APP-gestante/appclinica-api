from fastapi import APIRouter
from app.api.v1 import auth, users, appointments, vitals, exams, superadmin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(appointments.router, tags=["appointments"])
api_router.include_router(vitals.router, prefix="/patients", tags=["vitals"])
api_router.include_router(exams.router, prefix="/patients", tags=["exams"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["superadmin"])
