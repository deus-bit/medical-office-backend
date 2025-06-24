from app.base.models import BaseModel, Field
from datetime import datetime
from typing import Annotated

class PrescriptionRequestSchema(BaseModel):
    patient_id: Annotated[int, Field(gt=0)]
    doctor_id: Annotated[int, Field(gt=0)]
    medical_diagnosis_id: Annotated[int, Field(gt=0)]
    canceled: Annotated[bool, Field(default=False)]

class PrescriptionResponseSchema(PrescriptionRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]
