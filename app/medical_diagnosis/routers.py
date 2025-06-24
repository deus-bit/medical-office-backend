from fastapi import APIRouter, HTTPException, status, Path, Query, Body
from app.medical_diagnosis.repositories import MedicalDiagnosisFindQuery
from app.medical_diagnosis.services import MedicalDiagnosisService
from app.medical_diagnosis.schemas import MedicalDiagnosisRequestSchema, MedicalDiagnosisResponseSchema
from app.medical_diagnosis.models import MedicalDiagnosisModel
from app.exceptions import *
from app.base.models import Page
from app.utils import Positive, parse_last_retrieved
from collections.abc import Callable
from typing import Annotated
from datetime import datetime

class MedicalDiagnosisRouter(APIRouter):
    def __init__(self, prefix: str, diagnosis_service_factory: Callable[[], MedicalDiagnosisService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = diagnosis_service_factory

        self.add_api_route('/', self.post_diagnosis, name="Post Medical Diagnosis", methods=['post'])
        self.add_api_route('/find', self.find_diagnoses, name="Find Medical Diagnoses", methods=['post'])

        self.add_api_route('/{id}', self.get_diagnosis, name="Get Medical Diagnosis", methods=['get'])
        self.add_api_route('/{id}', self.put_diagnosis, name="Put Medical Diagnosis", methods=['put'])
        self.add_api_route('/{id}', self.delete_diagnosis, name="Delete Medical Diagnosis", methods=['delete'])

        self.add_api_route('/{id}/created_at', self.get_diagnosis_created_at, name="Get Diagnosis Registration Date", methods=['get'])
        self.add_api_route('/{id}/patient_id', self.get_diagnosis_patient_id, name="Get Diagnosis Patient ID", methods=['get'])
        self.add_api_route('/{id}/doctor_id', self.get_diagnosis_doctor_id, name="Get Diagnosis Doctor ID", methods=['get'])
        self.add_api_route('/{id}/disease', self.get_diagnosis_disease, name="Get Diagnosis Disease", methods=['get'])

        self.add_api_route('/{id}/patient_id', self.put_diagnosis_patient_id, name="Put Diagnosis Patient ID", methods=['put'])
        self.add_api_route('/{id}/doctor_id', self.put_diagnosis_doctor_id, name="Put Diagnosis Doctor ID", methods=['put'])
        self.add_api_route('/{id}/disease', self.put_diagnosis_disease, name="Put Diagnosis Disease", methods=['put'])

    async def post_diagnosis(self, diagnosis: Annotated[MedicalDiagnosisRequestSchema, Body()]) -> MedicalDiagnosisResponseSchema:
        return MedicalDiagnosisResponseSchema.model_validate((await self.svc().add(MedicalDiagnosisModel.model_validate(diagnosis))).model_dump())

    async def get_diagnosis(self, id: Annotated[Positive[int], Path()]) -> MedicalDiagnosisResponseSchema:
        try:
            diagnosis: MedicalDiagnosisModel | None = await self.svc().find_by_id(id)
            if diagnosis:
                return MedicalDiagnosisResponseSchema.model_validate(diagnosis)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_diagnoses(self, query: Annotated[MedicalDiagnosisFindQuery, Body()]) -> Page[MedicalDiagnosisResponseSchema, MedicalDiagnosisFindQuery] | None:
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), MedicalDiagnosisModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page = Page[MedicalDiagnosisResponseSchema, MedicalDiagnosisFindQuery](
                next=page.next,
                data=[MedicalDiagnosisResponseSchema.model_validate(diagnosis) for diagnosis in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_diagnosis(self, id: Annotated[Positive[int], Path()], diagnosis: Annotated[MedicalDiagnosisRequestSchema, Body()]) -> MedicalDiagnosisResponseSchema:
        try:
            model = await self.svc().update(id, MedicalDiagnosisModel.model_validate(diagnosis))
            return MedicalDiagnosisResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def delete_diagnosis(self, id: Annotated[Positive[int], Path()]) -> MedicalDiagnosisResponseSchema:
        try:
            model = await self.svc().delete(id)
            return MedicalDiagnosisResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def get_diagnosis_created_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_created_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def get_diagnosis_patient_id(self, id: Annotated[Positive[int], Path()]) -> int:
        try:
            return await self.svc().get_patient_id(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def get_diagnosis_doctor_id(self, id: Annotated[Positive[int], Path()]) -> int:
        try:
            return await self.svc().get_doctor_id(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def get_diagnosis_disease(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_disease(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def put_diagnosis_patient_id(self, id: Annotated[Positive[int], Path()], patient_id: Annotated[int, Body()]) -> MedicalDiagnosisResponseSchema:
        try:
            return MedicalDiagnosisResponseSchema.model_validate(await self.svc().update_patient_id(id, patient_id))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def put_diagnosis_doctor_id(self, id: Annotated[Positive[int], Path()], doctor_id: Annotated[int, Body()]) -> MedicalDiagnosisResponseSchema:
        try:
            return MedicalDiagnosisResponseSchema.model_validate(await self.svc().update_doctor_id(id, doctor_id))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.")

    async def put_diagnosis_disease(self, id: Annotated[Positive[int], Path()], disease: Annotated[str, Body()]) -> MedicalDiagnosisResponseSchema:
        try:
            return MedicalDiagnosisResponseSchema.model_validate(await self.svc().update_disease(id, disease))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical diagnosis not found.") 