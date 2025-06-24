from app.prescription.repositories import PrescriptionRepository, PrescriptionFindQuery
from app.prescription.models import PrescriptionModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime

class PrescriptionService(BaseService[PrescriptionModel, PrescriptionRepository, PrescriptionFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        return prescription.created_at

    async def get_patient_id(self, id: Positive[int]) -> int:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        return prescription.patient_id

    async def get_doctor_id(self, id: Positive[int]) -> int:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        return prescription.doctor_id

    async def get_medical_diagnosis_id(self, id: Positive[int]) -> int:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        return prescription.medical_diagnosis_id

    async def is_canceled(self, id: Positive[int]) -> bool:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        return prescription.canceled

    async def update_patient_id(self, id: Positive[int], patient_id: int) -> PrescriptionModel:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        prescription.patient_id = patient_id
        return await self.repo.update(id, prescription)

    async def update_doctor_id(self, id: Positive[int], doctor_id: int) -> PrescriptionModel:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        prescription.doctor_id = doctor_id
        return await self.repo.update(id, prescription)

    async def update_medical_diagnosis_id(self, id: Positive[int], medical_diagnosis_id: int) -> PrescriptionModel:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        prescription.medical_diagnosis_id = medical_diagnosis_id
        return await self.repo.update(id, prescription)

    async def update_canceled(self, id: Positive[int], canceled: bool) -> PrescriptionModel:
        prescription: PrescriptionModel | None = await self.find_by_id(id)
        if not prescription:
            raise EntityNotFound()
        prescription.canceled = canceled
        return await self.repo.update(id, prescription)
