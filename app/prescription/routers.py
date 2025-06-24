from fastapi import APIRouter, HTTPException, status, Path, Query, Body
from app.prescription.repositories import PrescriptionFindQuery
from app.prescription.services import PrescriptionService
from app.prescription.schemas import PrescriptionRequestSchema, PrescriptionResponseSchema
from app.prescription.models import PrescriptionModel
from app.exceptions import *
from app.base.models import Page
from app.utils import Positive, parse_last_retrieved
from collections.abc import Callable
from typing import Annotated
from datetime import datetime

class PrescriptionRouter(APIRouter):
    def __init__(self, prefix: str, prescription_service_factory: Callable[[], PrescriptionService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = prescription_service_factory

        self.add_api_route('/', self.post_prescription, name="Post Prescription", methods=['post'])
        self.add_api_route('/find', self.find_prescriptions, name="Find Prescriptions", methods=['post'])

        self.add_api_route('/{id}', self.get_prescription, name="Get Prescription", methods=['get'])
        self.add_api_route('/{id}', self.put_prescription, name="Put Prescription", methods=['put'])
        self.add_api_route('/{id}', self.delete_prescription, name="Delete Prescription", methods=['delete'])

        self.add_api_route('/{id}/created_at', self.get_prescription_created_at, name="Get Prescription Registration Date", methods=['get'])
        self.add_api_route('/{id}/patient_id', self.get_prescription_patient_id, name="Get Prescription Patient ID", methods=['get'])
        self.add_api_route('/{id}/doctor_id', self.get_prescription_doctor_id, name="Get Prescription Doctor ID", methods=['get'])
        self.add_api_route('/{id}/medical_diagnosis_id', self.get_prescription_medical_diagnosis_id, name="Get Prescription Medical Diagnosis ID", methods=['get'])
        self.add_api_route('/{id}/canceled', self.get_prescription_canceled, name="Get Prescription Canceled", methods=['get'])

        self.add_api_route('/{id}/patient_id', self.put_prescription_patient_id, name="Put Prescription Patient ID", methods=['put'])
        self.add_api_route('/{id}/doctor_id', self.put_prescription_doctor_id, name="Put Prescription Doctor ID", methods=['put'])
        self.add_api_route('/{id}/medical_diagnosis_id', self.put_prescription_medical_diagnosis_id, name="Put Prescription Medical Diagnosis ID", methods=['put'])
        self.add_api_route('/{id}/canceled', self.put_prescription_canceled, name="Put Prescription Canceled", methods=['put'])

    async def post_prescription(self, prescription: Annotated[PrescriptionRequestSchema, Body()]) -> PrescriptionResponseSchema:
        return PrescriptionResponseSchema.model_validate((await self.svc().add(PrescriptionModel.model_validate(prescription))).model_dump())

    async def get_prescription(self, id: Annotated[Positive[int], Path()]) -> PrescriptionResponseSchema:
        try:
            prescription: PrescriptionModel | None = await self.svc().find_by_id(id)
            if prescription:
                return PrescriptionResponseSchema.model_validate(prescription)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_prescriptions(self, query: Annotated[PrescriptionFindQuery, Body()]) -> Page[PrescriptionResponseSchema, PrescriptionFindQuery] | None:
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), PrescriptionModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page = Page[PrescriptionResponseSchema, PrescriptionFindQuery](
                next=page.next,
                data=[PrescriptionResponseSchema.model_validate(prescription) for prescription in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_prescription(self, id: Annotated[Positive[int], Path()], prescription: Annotated[PrescriptionRequestSchema, Body()]) -> PrescriptionResponseSchema:
        try:
            model = await self.svc().update(id, PrescriptionModel.model_validate(prescription))
            return PrescriptionResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def delete_prescription(self, id: Annotated[Positive[int], Path()]) -> PrescriptionResponseSchema:
        try:
            model = await self.svc().delete(id)
            return PrescriptionResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def get_prescription_created_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_created_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def get_prescription_patient_id(self, id: Annotated[Positive[int], Path()]) -> int:
        try:
            return await self.svc().get_patient_id(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def get_prescription_doctor_id(self, id: Annotated[Positive[int], Path()]) -> int:
        try:
            return await self.svc().get_doctor_id(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def get_prescription_medical_diagnosis_id(self, id: Annotated[Positive[int], Path()]) -> int:
        try:
            return await self.svc().get_medical_diagnosis_id(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def get_prescription_canceled(self, id: Annotated[Positive[int], Path()]) -> bool:
        try:
            return await self.svc().is_canceled(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def put_prescription_patient_id(self, id: Annotated[Positive[int], Path()], patient_id: Annotated[int, Body()]) -> PrescriptionResponseSchema:
        try:
            return PrescriptionResponseSchema.model_validate(await self.svc().update_patient_id(id, patient_id))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def put_prescription_doctor_id(self, id: Annotated[Positive[int], Path()], doctor_id: Annotated[int, Body()]) -> PrescriptionResponseSchema:
        try:
            return PrescriptionResponseSchema.model_validate(await self.svc().update_doctor_id(id, doctor_id))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def put_prescription_medical_diagnosis_id(self, id: Annotated[Positive[int], Path()], medical_diagnosis_id: Annotated[int, Body()]) -> PrescriptionResponseSchema:
        try:
            return PrescriptionResponseSchema.model_validate(await self.svc().update_medical_diagnosis_id(id, medical_diagnosis_id))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")

    async def put_prescription_canceled(self, id: Annotated[Positive[int], Path()], canceled: Annotated[bool, Body()]) -> PrescriptionResponseSchema:
        try:
            return PrescriptionResponseSchema.model_validate(await self.svc().update_canceled(id, canceled))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found.")
