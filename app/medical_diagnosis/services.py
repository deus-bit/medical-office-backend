from app.medical_diagnosis.repositories import MedicalDiagnosisRepository, MedicalDiagnosisFindQuery
from app.medical_diagnosis.models import MedicalDiagnosisModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime

class MedicalDiagnosisService(BaseService[MedicalDiagnosisModel, MedicalDiagnosisRepository, MedicalDiagnosisFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        return diagnosis.created_at

    async def get_patient_id(self, id: Positive[int]) -> int:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        return diagnosis.patient_id

    async def get_doctor_id(self, id: Positive[int]) -> int:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        return diagnosis.doctor_id

    async def get_disease(self, id: Positive[int]) -> str:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        return diagnosis.disease

    async def update_patient_id(self, id: Positive[int], patient_id: int) -> MedicalDiagnosisModel:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        diagnosis.patient_id = patient_id
        return await self.repo.update(id, diagnosis)

    async def update_doctor_id(self, id: Positive[int], doctor_id: int) -> MedicalDiagnosisModel:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        diagnosis.doctor_id = doctor_id
        return await self.repo.update(id, diagnosis)

    async def update_disease(self, id: Positive[int], disease: str) -> MedicalDiagnosisModel:
        diagnosis: MedicalDiagnosisModel | None = await self.find_by_id(id)
        if not diagnosis:
            raise EntityNotFound()
        diagnosis.disease = disease
        return await self.repo.update(id, diagnosis)
