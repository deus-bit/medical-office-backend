from app.medicine.repositories import MedicineFindQuery
from app.medicine.schemas import MedicineRequestSchema, MedicineResponseSchema
from app.exceptions import *
from app.utils import HttpClient, HttpxClient
from tests.integration.base import BaseApiClient

class MedicineApiClient(BaseApiClient[MedicineRequestSchema, MedicineResponseSchema, MedicineFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(MedicineResponseSchema, host_url.rstrip('/') + '/v1/medicine', client)
