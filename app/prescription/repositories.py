from app.utils import Interval
from app.prescription.models import (
    PrescriptionModel, PrescriptionAttribute,
    MedicationScheduleModel, MedicationScheduleAttribute
)
from app.generics import *
from app.exceptions import *
from app.config import settings
from sqlmodel import create_engine
from datetime import datetime
from typing import override

class PrescriptionFilterBy(FilterBy, total=False):
    id: Interval[int]
    created_at: Interval[datetime]
    patient_id: Interval[int]
    doctor_id: Interval[int]
    medical_diagnosis_id: Interval[int]
    canceled: bool


class PrescriptionFindQuery(FindQuery[PrescriptionModel, PrescriptionFilterBy, PrescriptionAttribute]):
    ...


class PrescriptionRepository(BaseRepository[PrescriptionModel, PrescriptionFindQuery], ABC):
    ...


class InMemoryPrescriptionRepository(SQLRepository[PrescriptionModel, PrescriptionFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=PrescriptionModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabasePrescriptionRepository(SQLRepository[PrescriptionModel, PrescriptionFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=PrescriptionModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )


class MedicationScheduleFilterBy(FilterBy, total=False):
    id: Interval[int]
    prescription_id: Interval[int]
    schedule_id: Interval[int]
    medicine_id: Interval[int]
    amount: Interval[int]


class MedicationScheduleFindQuery(FindQuery[MedicationScheduleModel, MedicationScheduleFilterBy, MedicationScheduleAttribute]):
    ...


class MedicationScheduleRepository(BaseRepository[MedicationScheduleModel, MedicationScheduleFindQuery], ABC):
    ...


class InMemoryMedicationScheduleRepository(SQLRepository[MedicationScheduleModel, MedicationScheduleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=MedicationScheduleModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseMedicationScheduleRepository(SQLRepository[MedicationScheduleModel, MedicationScheduleFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=MedicationScheduleModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )
