from app.base.models import SQLModel, MappedColumn
from typing import Literal, Annotated
from datetime import datetime

MedicineAttribute = Literal['id', 'created_at', 'updated_at', 'name', 'description', 'intake_type', 'dose', 'measurement']

class MedicineModel(SQLModel, table=True):
    __tablename__: str = 'medicines'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=63)]
    description: Annotated[str, MappedColumn(max_length=511)]
    intake_type: Annotated[str, MappedColumn(max_length=31)]
    dose: Annotated[float, MappedColumn(gt=0)]
    measurement: Annotated[str, MappedColumn(max_length=31)]
