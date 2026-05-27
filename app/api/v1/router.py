from fastapi import APIRouter
from app.api.v1 import (
    auth, users, appointments, vitals, exams, patients, announcements, superadmin,
    lab_tests, medications, notifications, reminders, baby_names, fetal_development,
    messages,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(appointments.router, tags=["appointments"])
api_router.include_router(vitals.router, prefix="/patients", tags=["vitals"])
api_router.include_router(exams.router, prefix="/patients", tags=["exams"])
api_router.include_router(lab_tests.router, prefix="/patients", tags=["exams"])
api_router.include_router(medications.router, prefix="/patients", tags=["medications"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(reminders.router, prefix="/patients", tags=["reminders"])
api_router.include_router(baby_names.router, tags=["baby-names"])
api_router.include_router(fetal_development.router, tags=["fetal-development"])
api_router.include_router(messages.router, tags=["chat"])
api_router.include_router(patients.router, tags=["patients", "doctor", "secretary"])
api_router.include_router(announcements.router, tags=["announcements"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["superadmin"])
