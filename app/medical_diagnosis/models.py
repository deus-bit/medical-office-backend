from app.base.models import SQLModel, MappedColumn
from typing import Literal, Annotated
from datetime import datetime

MedicalDiagnosisAttribute = Literal['id', 'created_at', 'patient_id', 'doctor_id', 'disease']

class MedicalDiagnosisModel(SQLModel, table=True):
    __tablename__ = 'medical_diagnoses'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    patient_id: Annotated[int, MappedColumn(gt=0, foreign_key='accounts.id', index=True)]
    doctor_id: Annotated[int, MappedColumn(gt=0, foreign_key='accounts.id', index=True)]
    disease: Annotated[str, MappedColumn(max_length=255)]
