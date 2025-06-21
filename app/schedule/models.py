from typing import Literal, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime

ScheduleAttribute = Literal['id']

class ScheduleModel(SQLModel, table=True):
    __tablename__ = 'schedules'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]


ScheduleCycleAttribute = Literal['id', 'created_at', 'start', 'repeat_each', 'repetition_number', 'schedule_id']

class ScheduleCycleModel(SQLModel, table=True):
    __tablename__ = 'schedule_cycles'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    start: Annotated[datetime, Field()]
    repeat_each: Annotated[int, Field(gt=0)]
    repetition_number: Annotated[int, Field(ge=0)]
    schedule_id: Annotated[int, Field(gt=0, foreign_key='schedules.id')]
