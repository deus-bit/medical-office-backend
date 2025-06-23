from app.schedule.models import (
    ScheduleModel, ScheduleAttribute,
    ScheduleCycleModel, ScheduleCycleAttribute
)
from app.base.repositories import BaseRepository, SQLRepository
from app.base.models import FindQuery, FilterBy
from app.exceptions import *
from app.config import settings
from app.utils import Interval
from sqlmodel import create_engine
from datetime import datetime
from typing import override
from abc import ABC

class ScheduleFilterBy(FilterBy, total=False):
    id: Interval[int]


class ScheduleFindQuery(FindQuery[ScheduleFilterBy, ScheduleAttribute]):
    ...


class ScheduleRepository(BaseRepository[ScheduleModel, ScheduleFindQuery], ABC):
    ...


class InMemoryScheduleRepository(SQLRepository[ScheduleModel, ScheduleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ScheduleModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseScheduleRepository(SQLRepository[ScheduleModel, ScheduleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ScheduleModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )


class ScheduleCycleFilterBy(FilterBy, total=False):
    id: Interval[int]
    created_at: Interval[datetime]
    start: Interval[datetime]
    repeat_each: Interval[datetime]
    repetition_number: Interval[int]
    schedule_id: Interval[int]


class ScheduleCycleFindQuery(FindQuery[ScheduleCycleFilterBy, ScheduleCycleAttribute]):
    ...


class ScheduleCycleRepository(BaseRepository[ScheduleCycleModel, ScheduleCycleFindQuery], ABC):
    ...


class InMemoryScheduleCycleRepository(SQLRepository[ScheduleCycleModel, ScheduleCycleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ScheduleCycleModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseScheduleCycleRepository(SQLRepository[ScheduleCycleModel, ScheduleCycleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ScheduleCycleModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )
