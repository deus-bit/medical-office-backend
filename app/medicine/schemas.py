from app.base.models import BaseModel, Field
from datetime import datetime
from typing import Annotated

class MedicineRequestSchema(BaseModel):
    name: Annotated[str, Field(max_length=63)]
    description: Annotated[str, Field(max_length=511)]
    intake_type: Annotated[str, Field(max_length=31)]
    dose: Annotated[float, Field(gt=0)]
    measurement: Annotated[str, Field(max_length=23)]


class MedicineResponseSchema(MedicineRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]
    updated_at: Annotated[datetime, Field()]
