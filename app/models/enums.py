import enum

class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    patient = "patient"
    doctor = "doctor"
    secretary = "secretary"
    admin = "admin"

class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

class PatientAppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    reschedule_requested = "reschedule_requested"
    reschedule_approved = "reschedule_approved"

class AppointmentType(str, enum.Enum):
    routine = "routine"
    ultrasound = "ultrasound"
    lab = "lab"
    follow_up = "follow_up"
    emergency = "emergency"

class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class VitalClassification(str, enum.Enum):
    Normal = "Normal"
    Atenção = "Atenção"
    Alto = "Alto"

class TimeOfDay(str, enum.Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"
    night = "night"

class GlucoseMoment(str, enum.Enum):
    fasting = "fasting"
    after_meal = "after_meal"
    random = "random"

class FetalPresentation(str, enum.Enum):
    cephalic = "cephalic"
    breech = "breech"
    transverse = "transverse"

class UltrasoundType(str, enum.Enum):
    obstetric = "obstetric"
    morphology = "morphology"
    detailed = "detailed"

class VaccineStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    missed = "missed"

class SerologyStatus(str, enum.Enum):
    negative = "negative"
    positive = "positive"
    pending = "pending"

class StreptococoStatus(str, enum.Enum):
    negative = "negative"
    positive = "positive"
    pending = "pending"
    not_done = "not_done"

class AnnouncementCategory(str, enum.Enum):
    agenda = "agenda"
    saude = "saude"
    clinica = "clinica"
    geral = "geral"

class MessageSenderType(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"
    secretary = "secretary"
    system = "system"

class LabTestType(str, enum.Enum):
    hemograma = "hemograma"
    glicemia = "glicemia"
    urina = "urina"
    outros = "outros"

class LabTestStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    abnormal = "abnormal"

class NotificationType(str, enum.Enum):
    appointment_reminder = "appointment_reminder"
    clinic_announcement = "clinic_announcement"
    vital_alert = "vital_alert"

class ReminderType(str, enum.Enum):
    appointment = "appointment"
    exam = "exam"
    medication = "medication"

class BabyNameGender(str, enum.Enum):
    male = "male"
    female = "female"
    neutral = "neutral"

class NameTrend(str, enum.Enum):
    rising = "rising"
    stable = "stable"
    declining = "declining"
