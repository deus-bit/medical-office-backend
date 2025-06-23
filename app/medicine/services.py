from app.medicine.repositories import MedicineRepository, MedicineFindQuery
from app.medicine.models import MedicineModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime

class MedicineService(BaseService[MedicineModel, MedicineRepository, MedicineFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.created_at

    async def get_name(self, id: Positive[int]) -> str:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.name

    async def get_description(self, id: Positive[int]) -> str:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.description

    async def get_intake_type(self, id: Positive[int]) -> str:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.intake_type

    async def get_dose(self, id: Positive[int]) -> float:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.dose

    async def get_measurement(self, id: Positive[int]) -> str:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        return medicine.measurement

    async def update_name(self, id: Positive[int], name: str) -> MedicineModel:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        medicine.name = name
        return await self.repo.update(id, medicine)

    async def update_description(self, id: Positive[int], description: str) -> MedicineModel:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        medicine.description = description
        return await self.repo.update(id, medicine)

    async def update_intake_type(self, id: Positive[int], intake_type: str) -> MedicineModel:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        medicine.intake_type = intake_type
        return await self.repo.update(id, medicine)

    async def update_dose(self, id: Positive[int], dose: float) -> MedicineModel:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        medicine.dose = dose
        return await self.repo.update(id, medicine)

    async def update_measurement(self, id: Positive[int], measurement: str) -> MedicineModel:
        medicine: MedicineModel | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound()
        medicine.measurement = measurement
        return await self.repo.update(id, medicine)
