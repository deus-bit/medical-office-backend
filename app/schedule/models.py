from app.base.models import SQLModel, MappedColumn
from typing import Literal, Annotated
from datetime import datetime

ScheduleAttribute = Literal['id']

class ScheduleModel(SQLModel, table=True):
    __tablename__ = 'schedules'



ScheduleCycleAttribute = Literal['id', 'created_at', 'start', 'repeat_each', 'repetition_number', 'schedule_id']

class ScheduleCycleModel(SQLModel, table=True):
    __tablename__ = 'schedule_cycles'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    start: Annotated[datetime, MappedColumn()]
    repeat_each: Annotated[int, MappedColumn(gt=0)]
    repetition_number: Annotated[int, MappedColumn(ge=0)]
    schedule_id: Annotated[int, MappedColumn(gt=0, foreign_key='schedules.id')]
