from app.medicine.repositories import MedicineFindQuery
from app.medicine.schemas import MedicineRequestSchema, MedicineResponseSchema
from app.exceptions import *
from app.utils import HttpClient, HttpxClient
from tests.integration.base import BaseApiClient

class MedicineApiClient(BaseApiClient[MedicineRequestSchema, MedicineResponseSchema, MedicineFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(MedicineResponseSchema, host_url.rstrip('/') + '/v1/medicine', client)

    async def update_name(self, id: int, name: str) -> MedicineResponseSchema:
        medicine: MedicineResponseSchema | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound(f"Medicine with ID {id} not found.")
        medicine.name = name
        return await self.repo.update(id, medicine)

    async def update_description(self, id: int, description: str) -> MedicineResponseSchema:
        medicine: MedicineResponseSchema | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound(f"Medicine with ID {id} not found.")
        medicine.description = description
        return await self.repo.update(id, medicine)

    async def update_intake_type(self, id: int, intake_type: str) -> MedicineResponseSchema:
        medicine: MedicineResponseSchema | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound(f"Medicine with ID {id} not found.")
        medicine.intake_type = intake_type
        return await self.repo.update(id, medicine)

    async def update_dose(self, id: int, dose: float) -> MedicineResponseSchema:
        medicine: MedicineResponseSchema | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound(f"Medicine with ID {id} not found.")
        medicine.dose = dose
        return await self.repo.update(id, medicine)

    async def update_measurement(self, id: int, measurement: str) -> MedicineResponseSchema:
        medicine: MedicineResponseSchema | None = await self.find_by_id(id)
        if not medicine:
            raise EntityNotFound(f"Medicine with ID {id} not found.")
        medicine.measurement = measurement
        return await self.repo.update(id, medicine)
