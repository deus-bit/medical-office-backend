from fastapi import APIRouter, HTTPException, status, Path, Query, Body
from app.medicine.repositories import MedicineFindQuery
from app.medicine.services import MedicineService
from app.medicine.schemas import MedicineRequestSchema, MedicineResponseSchema
from app.medicine.models import MedicineModel
from app.exceptions import *
from app.base.models import Page
from app.utils import Positive, parse_last_retrieved
from collections.abc import Callable
from typing import Annotated
from datetime import datetime

class MedicineRouter(APIRouter):
    def __init__(self, prefix: str, medicine_service_factory: Callable[[], MedicineService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = medicine_service_factory

        self.add_api_route('/', self.post_medicine, name="Post Medicine", methods=['post'])
        self.add_api_route('/find', self.find_medicines, name="Find Medicines", methods=['post'])

        self.add_api_route('/{id}', self.get_medicine, name="Get Medicine", methods=['get'])
        self.add_api_route('/{id}', self.put_medicine, name="Put Medicine", methods=['put'])
        self.add_api_route('/{id}', self.delete_medicine, name="Delete Medicine", methods=['delete'])

        self.add_api_route('/{id}/created_at', self.get_medicine_created_at, name="Get Medicine Registration Date", methods=['get'])
        self.add_api_route('/{id}/name', self.get_medicine_name, name="Get Medicine Name", methods=['get'])
        self.add_api_route('/{id}/description', self.get_medicine_description, name="Get Medicine Description", methods=['get'])
        self.add_api_route('/{id}/intake_type', self.get_medicine_intake_type, name="Get Medicine Intake Type", methods=['get'])
        self.add_api_route('/{id}/dose', self.get_medicine_dose, name="Get Medicine Dose", methods=['get'])
        self.add_api_route('/{id}/measurement', self.get_medicine_measurement, name="Get Medicine Measurement", methods=['get'])

        self.add_api_route('/{id}/name', self.put_medicine_name, name="Put Medicine Name", methods=['put'])
        self.add_api_route('/{id}/description', self.put_medicine_description, name="Put Medicine Description", methods=['put'])
        self.add_api_route('/{id}/intake_type', self.put_medicine_intake_type, name="Put Medicine Intake Type", methods=['put'])
        self.add_api_route('/{id}/dose', self.put_medicine_dose, name="Put Medicine Dose", methods=['put'])
        self.add_api_route('/{id}/measurement', self.put_medicine_measurement, name="Put Medicine Measurement", methods=['put'])

    async def post_medicine(self, medicine: Annotated[MedicineRequestSchema, Body()]) -> MedicineResponseSchema:
        """
        ### Example
        ~~~json
        {
          "name": "Ibuprofeno",
          "description": "Analgésico y antiinflamatorio para el tratamiento del dolor y fiebre.",
          "intake_type": "Comprimido",
          "dose": 400,
          "measurement": "mg"
        }
        ~~~
        """
        return MedicineResponseSchema.model_validate((await self.svc().add(MedicineModel.model_validate(medicine))).model_dump())

    async def get_medicine(self, id: Annotated[Positive[int], Path()]) -> MedicineResponseSchema:
        """
        ### Examples
          - http://localhost:8000/v1/medicine/101?attr=name,description,created_at
          - http://localhost:8000/v1/medicine/102?attr=name
        """
        try:
            medicine: MedicineModel | None = await self.svc().find_by_id(id)
            if medicine:
                return MedicineResponseSchema.model_validate(medicine)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_medicines(self, query: Annotated[MedicineFindQuery, Body()]
                             ) -> Page[MedicineResponseSchema, MedicineFindQuery] | None:
        """
        ### Example
        url: http://localhost:8000/v1/medicine/find/?attr=name,description,created_at
        body:
        ~~~json
        {
            filter_by: {
                "intake_type": "Comprimido",
                "dose": {
                    "start": 400,
                    "end": 600,
                    "end_inclusive": true
                },
                "measurement": "mg"
            },
            order_by: ['name', 'asc']
        }
        ~~~
        """
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), MedicineModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page= Page[MedicineResponseSchema, MedicineFindQuery](
                next=page.next,
                data=[MedicineResponseSchema.model_validate(medicine) for medicine in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_medicine(self, id: Annotated[Positive[int], Path()],
                           medicine: Annotated[MedicineRequestSchema, Body()]
                           ) -> MedicineResponseSchema:
        try:
            return await self.svc().update(id, MedicineModel.model_validate(medicine))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def delete_medicine(self, id: Annotated[Positive[int], Path()]) -> MedicineResponseSchema:
        try:
            return await self.svc().delete(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_created_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_created_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_name(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_name(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_description(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_description(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_intake_type(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_intake_type(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_dose(self, id: Annotated[Positive[int], Path()]) -> float:
        try:
            return await self.svc().get_dose(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def get_medicine_measurement(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_measurement(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def put_medicine_name(self, id: Annotated[Positive[int], Path()],
                                name: Annotated[str, Body()]
                                ) -> MedicineResponseSchema:
        try:
            return MedicineResponseSchema.model_validate(await self.svc().update_name(id, name))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def put_medicine_description(self, id: Annotated[Positive[int], Path()],
                                       description: Annotated[str, Body()]
                                       ) -> MedicineResponseSchema:
        try:
            return MedicineResponseSchema.model_validate(await self.svc().update_description(id, description))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def put_medicine_intake_type(self, id: Annotated[Positive[int], Path()],
                                       intake_type: Annotated[str, Body()]
                                       ) -> MedicineResponseSchema:
        try:
            return MedicineResponseSchema.model_validate(await self.svc().update_intake_type(id, intake_type))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def put_medicine_dose(self, id: Annotated[Positive[int], Path()],
                                dose: Annotated[float, Body()]
                                ) -> MedicineResponseSchema:
        try:
            return MedicineResponseSchema.model_validate(await self.svc().update_dose(id, dose))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")

    async def put_medicine_measurement(self, id: Annotated[Positive[int], Path()],
                                       measurement: Annotated[str, Body()]
                                       ) -> MedicineResponseSchema:
        try:
            return MedicineResponseSchema.model_validate(await self.svc().update_measurement(id, measurement))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found.")
