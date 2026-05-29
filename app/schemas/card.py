from typing import Optional, List, Any, Dict
from uuid import UUID
from app.schemas.base import CoreModel, BaseEntitySchema


# ── Template do médico ────────────────────────────────────────────────────────

class CardSectionCreate(CoreModel):
    title: str
    section_type: str  # 'text' | 'fields' (builtin só via init)

class CardSectionUpdate(CoreModel):
    title: Optional[str] = None
    visible: Optional[bool] = None

class CardSectionResponse(BaseEntitySchema):
    doctor_id: UUID
    title: str
    section_type: str
    builtin_key: Optional[str] = None
    position: int
    visible: bool

class CardMoveRequest(CoreModel):
    direction: str  # 'up' | 'down'


# ── Conteúdo por paciente ─────────────────────────────────────────────────────

class CardFieldValue(CoreModel):
    label: str
    value: Optional[str] = None
    position: int = 0

class CardEntryUpsert(CoreModel):
    content: Optional[str] = None          # para seções 'text'
    fields: Optional[List[CardFieldValue]] = None  # para seções 'fields'


# ── Cartão renderizado (GET /patients/{id}/card) ──────────────────────────────

class RenderedCardSection(CoreModel):
    section_id: UUID
    title: str
    section_type: str
    builtin_key: Optional[str] = None
    position: int
    visible: bool
    content: Optional[str] = None
    fields: Optional[List[CardFieldValue]] = None
    builtin_data: Optional[Dict[str, Any]] = None  # dados automáticos para seções built-in

class PatientCardResponse(CoreModel):
    patient_id: UUID
    doctor_id: UUID
    sections: List[RenderedCardSection]
