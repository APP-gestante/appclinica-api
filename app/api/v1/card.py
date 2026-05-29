from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.crud import card as crud_card
from app.schemas.card import (
    CardSectionCreate, CardSectionUpdate, CardSectionResponse,
    CardMoveRequest, CardEntryUpsert, PatientCardResponse,
)

router = APIRouter()


# ── Template do médico ────────────────────────────────────────────────────────

@router.get("/doctors/{doctor_id}/card-template", response_model=List[CardSectionResponse], tags=["card"])
async def get_template(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Retorna (e inicializa se necessário) o template de cartão do médico."""
    return await crud_card.init_template(db, doctor_id=doctor_id)


@router.post("/doctors/{doctor_id}/card-template/sections", response_model=CardSectionResponse, tags=["card"])
async def add_section(
    doctor_id: UUID,
    obj_in: CardSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Adiciona nova seção customizada ao template."""
    if obj_in.section_type not in ("text", "fields"):
        raise HTTPException(status_code=400, detail="Só é permitido criar seções do tipo 'text' ou 'fields'")
    return await crud_card.add_section(db, doctor_id=doctor_id, obj_in=obj_in)


@router.patch("/doctors/{doctor_id}/card-template/sections/{section_id}", response_model=CardSectionResponse, tags=["card"])
async def update_section(
    doctor_id: UUID,
    section_id: UUID,
    obj_in: CardSectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Atualiza título ou visibilidade de uma seção."""
    section = await crud_card.get_section(db, section_id=section_id, doctor_id=doctor_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return await crud_card.update_section(db, section=section, obj_in=obj_in)


@router.post("/doctors/{doctor_id}/card-template/sections/{section_id}/move", response_model=List[CardSectionResponse], tags=["card"])
async def move_section(
    doctor_id: UUID,
    section_id: UUID,
    obj_in: CardMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Move uma seção para cima ou para baixo na ordem."""
    if obj_in.direction not in ("up", "down"):
        raise HTTPException(status_code=400, detail="direction deve ser 'up' ou 'down'")
    return await crud_card.move_section(db, doctor_id=doctor_id, section_id=section_id, direction=obj_in.direction)


@router.delete("/doctors/{doctor_id}/card-template/sections/{section_id}", status_code=204, tags=["card"])
async def delete_section(
    doctor_id: UUID,
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Remove uma seção customizada (built-in não pode ser removida)."""
    section = await crud_card.get_section(db, section_id=section_id, doctor_id=doctor_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    if section.section_type == "builtin":
        raise HTTPException(status_code=400, detail="Seções built-in não podem ser removidas, apenas ocultadas")
    await crud_card.delete_section(db, section=section)


# ── Cartão por paciente ───────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/card", response_model=PatientCardResponse, tags=["card"])
async def get_patient_card(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna o cartão completo da gestante: template + dados built-in + conteúdo por paciente."""
    doctor_id = current_user.id
    rendered = await crud_card.render_patient_card(db, patient_id=patient_id, doctor_id=doctor_id)
    return rendered


@router.put("/patients/{patient_id}/card/sections/{section_id}", status_code=204, tags=["card"])
async def save_section_content(
    patient_id: UUID,
    section_id: UUID,
    obj_in: CardEntryUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["doctor", "admin"])),
):
    """Salva o conteúdo de uma seção para um paciente específico."""
    await crud_card.upsert_entry(db, patient_id=patient_id, section_id=section_id, obj_in=obj_in)
