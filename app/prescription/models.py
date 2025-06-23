from app.base.models import SQLModel, MappedColumn
from typing import Literal, Annotated
from datetime import datetime

PrescriptionAttribute = Literal['id', 'created_at', 'patient_id', 'doctor_id']

class PrescriptionModel(SQLModel, table=True):
    __tablename__ = 'prescriptions'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    patient_id: Annotated[int, MappedColumn(gt=0, foreign_key='accounts.id', index=True)]
    doctor_id: Annotated[int, MappedColumn(gt=0, foreign_key='accounts.id', index=True)]
    medical_diagnosis_id: Annotated[int, MappedColumn(gt=0, foreign_key='medical_diagnoses.id', index=True)]
    canceled: Annotated[bool, MappedColumn(False)]


MedicationScheduleAttribute = Literal['id']

class MedicationScheduleModel(SQLModel, table=True):
    __tablename__ = 'medication_schedules'

    prescription_id: Annotated[int, MappedColumn(gt=0, foreign_key='prescriptions.id', index=True)]
    schedule_id: Annotated[int, MappedColumn(gt=0, foreign_key='schedules.id', index=True)]
    medicine_id: Annotated[int, MappedColumn(gt=0, foreign_key='medicines.id', index=True)]
    amount: Annotated[int, MappedColumn(gt=0)]
