from app.exceptions import *

from app.schedule.repositories import (
    ScheduleRepository, ScheduleFindQuery,
    InMemoryScheduleRepository,

    ScheduleCycleRepository, ScheduleCycleFindQuery,
    InMemoryScheduleCycleRepository,
)
from app.schedule.models import ScheduleModel, ScheduleCycleModel

from app.utils import HttpxClient
from datetime import datetime
import pytest

@pytest.mark.parametrize('schedule_repo,schedule_cycle_repo', [
    (InMemoryScheduleRepository(),
     InMemoryScheduleCycleRepository())
])
async def test_schedule_repository(schedule_repo: ScheduleRepository,
                                   schedule_cycle_repo: ScheduleCycleRepository,
                                   ) -> None:
    new_schedule = ScheduleModel()
    new_schedule = await schedule_repo.add(new_schedule)
    assert new_schedule.id is not None, "Schedule should have an ID after being added."

    stored_schedule = await schedule_repo.find_by_id(new_schedule.id)
    assert stored_schedule == new_schedule

    new_schedule_cycle = ScheduleCycleModel(
        start=datetime.now(),
        repeat_each=8,
        repetition_number=3 * 20,
        schedule_id=new_schedule.id,
    )
    new_schedule_cycle.schedule_id = new_schedule.id
    new_schedule_cycle = await schedule_cycle_repo.add(new_schedule_cycle)
    assert new_schedule_cycle.id is not None, "Schedule cycle should have an ID after being added."

    stored_schedule_cycle = await schedule_cycle_repo.find_by_id(new_schedule_cycle.id)
    assert stored_schedule_cycle == new_schedule_cycle
