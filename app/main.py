from fastapi import FastAPI
from app.medicine.repositories import InMemoryMedicineRepository
from app.medicine.services import MedicineService
from app.medicine.routers import MedicineRouter

class VidaPlenaAPI(FastAPI):
    def __init__(self) -> None:
        super().__init__()
        medicine_repository = InMemoryMedicineRepository()
        medicine_service_factory = lambda: MedicineService(medicine_repository)

        self.include_router(MedicineRouter('/v1/medicine', medicine_service_factory))


app = VidaPlenaAPI()
