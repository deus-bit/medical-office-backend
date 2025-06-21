from typing import Literal, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime

MedicalDiagnosisAttribute = Literal['id', 'created_at', 'patient_id', 'doctor_id', 'disease']

class MedicalDiagnosisModel(SQLModel, table=True):
    __tablename__ = 'medical_diagnoses'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    patient_id: Annotated[int, Field(gt=0, foreign_key='accounts.id', index=True)]
    doctor_id: Annotated[int, Field(gt=0, foreign_key='accounts.id', index=True)]
    disease: Annotated[str, Field(max_length=255)]
