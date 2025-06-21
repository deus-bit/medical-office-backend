from typing import Literal, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime

PrescriptionAttribute = Literal['id', 'created_at', 'patient_id', 'doctor_id']

class PrescriptionModel(SQLModel, table=True):
    __tablename__ = 'prescriptions'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    patient_id: Annotated[int, Field(gt=0, foreign_key='accounts.id', index=True)]
    doctor_id: Annotated[int, Field(gt=0, foreign_key='accounts.id', index=True)]
    medical_diagnosis_id: Annotated[int, Field(gt=0, foreign_key='medical_diagnoses.id', index=True)]
    canceled: Annotated[bool, Field(False)]


MedicationScheduleAttribute = Literal['id']

class MedicationScheduleModel(SQLModel, table=True):
    __tablename__ = 'medication_schedules'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    prescription_id: Annotated[int, Field(gt=0, foreign_key='prescriptions.id', index=True)]
    schedule_id: Annotated[int, Field(gt=0, foreign_key='schedules.id', index=True)]
    medicine_id: Annotated[int, Field(gt=0, foreign_key='medicines.id', index=True)]
    amount: Annotated[int, Field(gt=0)]
