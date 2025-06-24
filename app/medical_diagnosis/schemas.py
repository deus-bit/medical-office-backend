from app.base.models import BaseModel, Field
from datetime import datetime
from typing import Annotated

class MedicalDiagnosisRequestSchema(BaseModel):
    patient_id: Annotated[int, Field(gt=0)]
    doctor_id: Annotated[int, Field(gt=0)]
    disease: Annotated[str, Field(max_length=255)]

class MedicalDiagnosisResponseSchema(MedicalDiagnosisRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]
