from app.exceptions import EntityNotFound
from app.medicine.repositories import (
    MedicineRepository, MedicineFindQuery,
    InMemoryMedicineRepository,
    # SupabaseMedicineRepository,
)
from app.medicine.services import MedicineService
from app.medicine.models import MedicineModel
from app.utils import HttpxClient
from tests.utils import HttpClientService
from random import randint
import pytest

def get_medicines() -> list[MedicineModel]:
    return [
        MedicineModel(
            name="Aciclovir",
            description="Antiviral utilizado para tratar infecciones por herpes.",
            intake_type="Comprimido",
            dose=400,
            measurement="mg"
        ),
        MedicineModel(
            name="Albendazol",
            description="Antihelmíntico empleado en el tratamiento de infecciones por gusanos intestinales.",
            intake_type="Comprimido masticable",
            dose=400,
            measurement="mg"
        ),
        MedicineModel(
            name="Amlodipino",
            description="Antihipertensivo utilizado para controlar la presión arterial alta.",
            intake_type="Comprimido",
            dose=10,
            measurement="mg"
        ),
        MedicineModel(
            name="Amoxicilina",
            description="Antibiótico de amplio espectro para infecciones bacterianas.",
            intake_type="Comprimido",
            dose=1,
            measurement="g"
        ),
        MedicineModel(
            name="Atorvastatina",
            description="Medicamento hipocolesterolémico para reducir niveles de colesterol.",
            intake_type="Comprimido",
            dose=20,
            measurement="mg"
        ),
        MedicineModel(
            name="Azitromicina",
            description="Antibiótico macrólido utilizado en diversas infecciones bacterianas.",
            intake_type="Comprimido",
            dose=1,
            measurement="g"
        ),
        MedicineModel(
            name="Clorfeniramina",
            description="Antihistamínico para aliviar síntomas de alergias.",
            intake_type="Comprimido",
            dose=4,
            measurement="mg"
        ),
        MedicineModel(
            name="Diclofenaco Sódico",
            description="Antiinflamatorio no esteroideo para aliviar dolor e inflamación.",
            intake_type="Comprimido",
            dose=50,
            measurement="mg"
        ),
        MedicineModel(
            name="Ibuprofeno",
            description="Analgésico y antiinflamatorio para el tratamiento del dolor y fiebre.",
            intake_type="Comprimido",
            dose=400,
            measurement="mg"
        ),
        MedicineModel(
            name="Salbutamol",
            description="Broncodilatador utilizado en el tratamiento del asma y otras afecciones pulmonares.",
            intake_type="Aerosol",
            dose=100,
            measurement="μg/inhalación"
        )
    ][:]

@pytest.mark.parametrize('repo', [
    InMemoryMedicineRepository(),
    MedicineService(InMemoryMedicineRepository()),
    HttpClientService[MedicineModel, MedicineFindQuery](MedicineModel, 'http://127.0.0.1:8000/v1/medicine'),
    # MedicineService(SupabaseMedicineRepository()),
    # SupabaseMedicineRepository(),
])
async def test_common_operations(repo: MedicineRepository | MedicineService) -> None:
    medicines = get_medicines()

    for id, medicine in enumerate(medicines, 1):
        stored_medicine = await repo.add(medicine)
        medicine.id = id
        assert stored_medicine == medicine

    for medicine in medicines:
        stored_medicine = await repo.find_by_id(medicine.id)
        assert stored_medicine == medicine

    count = 0
    page = await repo.find(MedicineFindQuery(order_by=('id', 'asc')))
    assert page != None
    while page:
        count += len(page.data)
        for stored_medicine in page.data:
            assert stored_medicine == medicines[stored_medicine.id - 1]
        page = await repo.find(page.next)
    assert count == len(medicines)

    count = 0
    page = await repo.find(MedicineFindQuery(order_by=('created_at', 'desc')))
    assert page != None
    while page:
        count += len(page.data)
        assert page.next.last == page.data[-1]
        for i in range(1, len(page.data)):
            assert page.data[i - 1].created_at > page.data[i].created_at or (
                page.data[i - 1].created_at == page.data[i].created_at and
                page.data[i - 1].id > page.data[i].id
            )
        page = await repo.find(page.next)
    assert count == len(medicines)

    medicine = medicines[randint(0, len(medicines) - 1)]
    medicine.description = "New description"
    stored_medicine = await repo.update(medicine.id, medicine)
    assert stored_medicine == medicine

    await repo.delete(medicine.id)
    assert await repo.find_by_id(medicine.id) is None

# def test_medicine_service() -> None:
#     svc = MedicineService(InMemoryMedicineRepository())

# def test_medicine_router() -> None:
#     client = HttpxClient()
#     for medicine in medicines:
#         client.post('http://localhost:8000/v1/medicine', medicine.model_dump())
