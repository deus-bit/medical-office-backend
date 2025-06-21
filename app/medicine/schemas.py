from app.utils import Positive
from typing import Annotated
from pydantic import BaseModel, Field

class MedicineRequestSchema(BaseModel):
    name: Annotated[str, Field(max_length=63)]
    description: Annotated[str, Field(max_length=511)]
    intake_type: Annotated[str, Field(max_length=31)]
    dose: Positive[float]
    measurement: Annotated[str, Field(max_length=23)]


class MedicineResponseSchema(MedicineRequestSchema):
    id: int
    created_at: str
    updated_at: str
