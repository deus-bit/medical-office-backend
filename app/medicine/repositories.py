from app.utils import Interval, RegEx
from app.medicine.models import MedicineModel, MedicineAttribute
from app.generics import *
from app.exceptions import *
from app.config import settings
from sqlmodel import create_engine
from datetime import datetime
from typing import override

class MedicineFilterBy(FilterBy, total=False):
    id: Interval[int]
    created_at: Interval[datetime]
    name: RegEx
    description: RegEx
    intake_type: RegEx
    dose: Interval[float]
    measurement: RegEx


class MedicineFindQuery(FindQuery[MedicineModel, MedicineFilterBy, MedicineAttribute]):
    ...


class MedicineRepository(BaseRepository[MedicineModel, MedicineFindQuery], ABC):
    ...


class InMemoryMedicineRepository(SQLRepository[MedicineModel, MedicineFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=MedicineModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseMedicineRepository(SQLRepository[MedicineModel, MedicineFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=MedicineModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )
