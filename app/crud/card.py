from uuid import UUID
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc

from app.models.card import DoctorCardSection, PatientCardEntry, PatientCardFieldValue
from app.models.user import Patient
from app.models.appointment_evolution import AppointmentEvolution
from app.models.lab_tests import LabTest
from app.models.exams import Vaccine
from app.models.medications import Medication
from app.models.patient_anamnesis import PatientAnamnesis
from app.schemas.card import CardSectionCreate, CardSectionUpdate, CardEntryUpsert, CardFieldValue

DEFAULT_SECTIONS = [
    {"title": "Dados Gestacionais",     "section_type": "builtin", "builtin_key": "dados_gestacionais", "position": 0},
    {"title": "Evolução das Consultas", "section_type": "builtin", "builtin_key": "evolucao",           "position": 1},
    {"title": "Exames Laboratoriais",   "section_type": "builtin", "builtin_key": "exames",             "position": 2},
    {"title": "Vacinas",                "section_type": "builtin", "builtin_key": "vacinas",            "position": 3},
    {"title": "Medicamentos",           "section_type": "builtin", "builtin_key": "medicamentos",       "position": 4},
    {"title": "Observações Clínicas",   "section_type": "text",    "builtin_key": None,                 "position": 5},
]


async def get_template(db: AsyncSession, doctor_id: UUID) -> List[DoctorCardSection]:
    result = await db.execute(
        select(DoctorCardSection)
        .where(DoctorCardSection.doctor_id == doctor_id, DoctorCardSection.deleted_at.is_(None))
        .order_by(asc(DoctorCardSection.position))
    )
    return list(result.scalars().all())


async def init_template(db: AsyncSession, doctor_id: UUID) -> List[DoctorCardSection]:
    """Cria o template padrão se o médico ainda não tiver um."""
    existing = await get_template(db, doctor_id)
    if existing:
        return existing
    sections = []
    for d in DEFAULT_SECTIONS:
        s = DoctorCardSection(doctor_id=doctor_id, **d, visible=True)
        db.add(s)
        sections.append(s)
    await db.commit()
    for s in sections:
        await db.refresh(s)
    return sections


async def add_section(db: AsyncSession, doctor_id: UUID, obj_in: CardSectionCreate) -> DoctorCardSection:
    existing = await get_template(db, doctor_id)
    position = max((s.position for s in existing), default=-1) + 1
    section = DoctorCardSection(
        doctor_id=doctor_id,
        title=obj_in.title,
        section_type=obj_in.section_type,
        builtin_key=None,
        position=position,
        visible=True,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


async def update_section(db: AsyncSession, section: DoctorCardSection, obj_in: CardSectionUpdate) -> DoctorCardSection:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    await db.commit()
    await db.refresh(section)
    return section


async def move_section(db: AsyncSession, doctor_id: UUID, section_id: UUID, direction: str) -> List[DoctorCardSection]:
    sections = await get_template(db, doctor_id)
    idx = next((i for i, s in enumerate(sections) if s.id == section_id), None)
    if idx is None:
        return sections
    if direction == "up" and idx > 0:
        sections[idx].position, sections[idx - 1].position = sections[idx - 1].position, sections[idx].position
    elif direction == "down" and idx < len(sections) - 1:
        sections[idx].position, sections[idx + 1].position = sections[idx + 1].position, sections[idx].position
    await db.commit()
    return await get_template(db, doctor_id)


async def delete_section(db: AsyncSession, section: DoctorCardSection) -> None:
    from datetime import datetime, timezone
    section.deleted_at = datetime.now(timezone.utc)
    await db.commit()


async def get_section(db: AsyncSession, section_id: UUID, doctor_id: UUID) -> Optional[DoctorCardSection]:
    result = await db.execute(
        select(DoctorCardSection).where(
            DoctorCardSection.id == section_id,
            DoctorCardSection.doctor_id == doctor_id,
            DoctorCardSection.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def upsert_entry(db: AsyncSession, patient_id: UUID, section_id: UUID, obj_in: CardEntryUpsert) -> None:
    # Para seções 'text'
    if obj_in.content is not None:
        result = await db.execute(
            select(PatientCardEntry).where(
                PatientCardEntry.patient_id == patient_id,
                PatientCardEntry.section_id == section_id,
                PatientCardEntry.deleted_at.is_(None),
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.content = obj_in.content
        else:
            entry = PatientCardEntry(patient_id=patient_id, section_id=section_id, content=obj_in.content)
            db.add(entry)

    # Para seções 'fields'
    if obj_in.fields is not None:
        result = await db.execute(
            select(PatientCardFieldValue).where(
                PatientCardFieldValue.patient_id == patient_id,
                PatientCardFieldValue.section_id == section_id,
            )
        )
        existing_fields = list(result.scalars().all())
        for f in existing_fields:
            await db.delete(f)
        for i, fv in enumerate(obj_in.fields):
            fv_obj = PatientCardFieldValue(
                patient_id=patient_id, section_id=section_id,
                label=fv.label, value=fv.value, position=i,
            )
            db.add(fv_obj)

    await db.commit()


async def _builtin_data(db: AsyncSession, key: str, patient_id: UUID, patient: Patient) -> dict:
    """Busca dados automáticos para seções built-in."""
    if key == "dados_gestacionais":
        lmp = patient.lmp_date
        today = date.today()
        current_week = ((today - lmp).days // 7) if lmp else patient.current_week
        return {
            "lmp_date": str(lmp) if lmp else None,
            "edd": str(patient.edd) if patient.edd else None,
            "current_week": current_week,
            "blood_type": patient.blood_type,
            "height_cm": patient.height_cm,
            "weight_initial_kg": patient.weight_initial_kg,
            "risk_level": str(patient.risk_level.value) if patient.risk_level else None,
            "hospital": patient.hospital,
            "number_of_fetuses": patient.number_of_fetuses,
            "parity": patient.parity,
        }
    if key == "evolucao":
        evos = (await db.execute(
            select(AppointmentEvolution)
            .where(AppointmentEvolution.patient_id == patient_id, AppointmentEvolution.deleted_at.is_(None))
            .order_by(asc(AppointmentEvolution.created_at))
        )).scalars().all()
        return {"evolutions": [
            {"date": str(e.created_at.date()), "weight_kg": str(e.weight_kg) if e.weight_kg else None,
             "bp": f"{e.bp_systolic}/{e.bp_diastolic}" if e.bp_systolic else None,
             "fundal_height_cm": str(e.fundal_height_cm) if e.fundal_height_cm else None,
             "fetal_heart_rate": e.fetal_heart_rate, "edema": e.edema,
             "presentation": str(e.presentation.value) if e.presentation else None,
             "clinical_notes": e.clinical_notes}
            for e in evos
        ]}
    if key == "exames":
        items = (await db.execute(
            select(LabTest).where(LabTest.patient_id == patient_id, LabTest.deleted_at.is_(None))
            .order_by(LabTest.date)
        )).scalars().all()
        return {"exames": [{"name": i.name, "date": str(i.date), "status": str(i.status.value), "result": i.result} for i in items]}
    if key == "vacinas":
        items = (await db.execute(
            select(Vaccine).where(Vaccine.patient_id == patient_id, Vaccine.deleted_at.is_(None))
        )).scalars().all()
        return {"vacinas": [{"type": i.vaccine_type, "dose": i.dose_number, "date": str(i.date), "status": str(i.status.value)} for i in items]}
    if key == "medicamentos":
        items = (await db.execute(
            select(Medication).where(
                Medication.patient_id == patient_id,
                Medication.deleted_at.is_(None),
                Medication.active == True,
            )
        )).scalars().all()
        return {"medicamentos": [{"name": i.name, "dosage": i.dosage, "frequency": i.frequency} for i in items]}
    if key == "anamnese":
        ana = (await db.execute(
            select(PatientAnamnesis).where(PatientAnamnesis.patient_id == patient_id, PatientAnamnesis.deleted_at.is_(None))
        )).scalar_one_or_none()
        if not ana:
            return {}
        return {
            "has_diabetes": ana.has_diabetes, "has_hipertensao": ana.has_hipertensao,
            "alergias_medicamentos": ana.alergias_medicamentos, "outras_alergias": ana.outras_alergias,
            "tabagismo": ana.tabagismo, "alcool": ana.alcool, "alcool_frequencia": ana.alcool_frequencia,
            "pre_eclampsia_anterior": ana.pre_eclampsia_anterior,
        }
    return {}


async def render_patient_card(db: AsyncSession, patient_id: UUID, doctor_id: UUID) -> dict:
    """Monta o cartão completo: template + conteúdo por paciente + dados built-in."""
    # Inicializa template se necessário
    sections = await init_template(db, doctor_id)

    # Carrega paciente
    patient = (await db.execute(select(Patient).where(Patient.id == patient_id))).scalar_one_or_none()
    if not patient:
        return {"patient_id": str(patient_id), "doctor_id": str(doctor_id), "sections": []}

    # Carrega entradas de texto por paciente
    entries = (await db.execute(
        select(PatientCardEntry).where(
            PatientCardEntry.patient_id == patient_id,
            PatientCardEntry.deleted_at.is_(None),
        )
    )).scalars().all()
    entry_map = {str(e.section_id): e.content for e in entries}

    # Carrega campos por paciente
    fields = (await db.execute(
        select(PatientCardFieldValue)
        .where(PatientCardFieldValue.patient_id == patient_id)
        .order_by(asc(PatientCardFieldValue.position))
    )).scalars().all()
    fields_map: dict = {}
    for f in fields:
        key = str(f.section_id)
        if key not in fields_map:
            fields_map[key] = []
        fields_map[key].append({"label": f.label, "value": f.value, "position": f.position})

    rendered = []
    for s in sections:
        sid = str(s.id)
        section_data = {
            "section_id": str(s.id),
            "title": s.title,
            "section_type": s.section_type,
            "builtin_key": s.builtin_key,
            "position": s.position,
            "visible": s.visible,
            "content": entry_map.get(sid),
            "fields": fields_map.get(sid),
            "builtin_data": await _builtin_data(db, s.builtin_key, patient_id, patient) if s.builtin_key else None,
        }
        rendered.append(section_data)

    return {"patient_id": str(patient_id), "doctor_id": str(doctor_id), "sections": rendered}
