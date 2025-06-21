from typing import Literal, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime

MedicineAttribute = Literal['id', 'created_at', 'name', 'description', 'intake_type', 'dose', 'measurement']

class MedicineModel(SQLModel, table=True):
    __tablename__ = 'medicines'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    name: Annotated[str, Field(max_length=63)]
    description: Annotated[str, Field(max_length=511)]
    intake_type: Annotated[str, Field(max_length=31)]
    dose: Annotated[float, Field(gt=0)]
    measurement: Annotated[str, Field(max_length=31)]
