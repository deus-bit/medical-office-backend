from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.medicine.repositories import InMemoryMedicineRepository
from app.medicine.services import MedicineService
from app.medicine.routers import MedicineRouter

class MedicalOfficeAPI(FastAPI):
    def __init__(self) -> None:
        super().__init__()

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        medicine_repository = InMemoryMedicineRepository()
        medicine_service_factory = lambda: MedicineService(medicine_repository)

        self.include_router(MedicineRouter('/v1/medicine', medicine_service_factory))


app = MedicalOfficeAPI()
