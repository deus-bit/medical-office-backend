from app.medicine.repositories import MedicineRepository, MedicineFindQuery
from app.medicine.models import MedicineAttribute, MedicineModel
from app.generics import Page
from app.utils import Positive
from datetime import datetime

class MedicineService:
    def __init__(self, medicine_repository: MedicineRepository) -> None:
        self.repo = medicine_repository

    async def add(self, medicine: MedicineModel) -> MedicineModel:
        return await self.repo.add(medicine)

    async def find(self, query: MedicineFindQuery) -> Page[MedicineModel, MedicineFindQuery] | None:
        return await self.repo.find(query)

    async def find_by_id(self, id: Positive[int]) -> MedicineModel:
        return await self.repo.find_by_id(id)

    async def update(self, id: Positive[int], medicine: MedicineModel) -> MedicineModel:
        return await self.repo.update(id, medicine)

    async def delete(self, id: Positive[int]) -> MedicineModel:
        return await self.repo.delete(id)

    async def upsert(self, medicine: MedicineModel) -> MedicineModel:
        return await self.repo.upsert(medicine)

    async def get_created_at(self, id: Positive[int]) -> datetime:
        return (await self.find_by_id(id)).created_at

    async def get_name(self, id: Positive[int]) -> str:
        return (await self.find_by_id(id)).name
    
    async def get_description(self, id: Positive[int]) -> str:
        return (await self.find_by_id(id)).description

    async def get_intake_type(self, id: Positive[int]) -> str:
        return (await self.find_by_id(id)).intake_type

    async def get_dose(self, id: Positive[int]) -> float:
        return (await self.find_by_id(id)).dose

    async def get_measurement(self, id: Positive[int]) -> str:
        return (await self.find_by_id(id)).measurement

    async def update_name(self, id: Positive[int], name: str) -> MedicineModel:
        medicine = await self.find_by_id(id)
        medicine.name = name
        return await self.repo.update(id, medicine)

    async def update_description(self, id: Positive[int], description: str) -> MedicineModel:
        medicine = await self.find_by_id(id)
        medicine.description = description
        return await self.repo.update(id, medicine)

    async def update_intake_type(self, id: Positive[int], intake_type: str) -> MedicineModel:
        medicine = await self.find_by_id(id)
        medicine.intake_type = intake_type
        return await self.repo.update(id, medicine)

    async def update_dose(self, id: Positive[int], dose: float) -> MedicineModel:
        medicine = await self.find_by_id(id)
        medicine.dose = dose
        return await self.repo.update(id, medicine)

    async def update_measurement(self, id: Positive[int], measurement: str) -> MedicineModel:
        medicine = await self.find_by_id(id)
        medicine.measurement = measurement
        return await self.repo.update(id, medicine)
