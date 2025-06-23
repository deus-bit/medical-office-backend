from app.medicine.repositories import (
    MedicineFindQuery,
    InMemoryMedicineRepository,
)
from app.medicine.services import MedicineService
from app.medicine.schemas import MedicineRequestSchema, MedicineResponseSchema
from app.medicine.models import MedicineModel
from app.base.common import SupportsModelPersistance
from app.base.models import Page
from tests.integration.medicine import MedicineApiClient
from random import randint
import pytest
from typing import Any

def get_medicines[T: MedicineModel | MedicineRequestSchema](model: type[T]) -> list[T]:
    return [
        model(
            name="Aciclovir",
            description="Antiviral utilizado para tratar infecciones por herpes.",
            intake_type="Comprimido",
            dose=400,
            measurement="mg"
        ),
        model(
            name="Albendazol",
            description="Antihelmíntico empleado en el tratamiento de infecciones por gusanos intestinales.",
            intake_type="Comprimido masticable",
            dose=400,
            measurement="mg"
        ),
        model(
            name="Amlodipino",
            description="Antihipertensivo utilizado para controlar la presión arterial alta.",
            intake_type="Comprimido",
            dose=10,
            measurement="mg"
        ),
        model(
            name="Amoxicilina",
            description="Antibiótico de amplio espectro para infecciones bacterianas.",
            intake_type="Comprimido",
            dose=1,
            measurement="g"
        ),
        model(
            name="Atorvastatina",
            description="Medicamento hipocolesterolémico para reducir niveles de colesterol.",
            intake_type="Comprimido",
            dose=20,
            measurement="mg"
        ),
        model(
            name="Azitromicina",
            description="Antibiótico macrólido utilizado en diversas infecciones bacterianas.",
            intake_type="Comprimido",
            dose=1,
            measurement="g"
        ),
        model(
            name="Clorfeniramina",
            description="Antihistamínico para aliviar síntomas de alergias.",
            intake_type="Comprimido",
            dose=4,
            measurement="mg"
        ),
        model(
            name="Diclofenaco Sódico",
            description="Antiinflamatorio no esteroideo para aliviar dolor e inflamación.",
            intake_type="Comprimido",
            dose=50,
            measurement="mg"
        ),
        model(
            name="Ibuprofeno",
            description="Analgésico y antiinflamatorio para el tratamiento del dolor y fiebre.",
            intake_type="Comprimido",
            dose=400,
            measurement="mg"
        ),
        model(
            name="Salbutamol",
            description="Broncodilatador utilizado en el tratamiento del asma y otras afecciones pulmonares.",
            intake_type="Aerosol",
            dose=100,
            measurement="μg/inhalación"
        )
    ][:]

@pytest.mark.parametrize('RequestSchema,ResponseSchema,mp', [
    (MedicineModel, MedicineModel, InMemoryMedicineRepository()),
    (MedicineModel, MedicineModel, MedicineService(InMemoryMedicineRepository())),
    (MedicineRequestSchema, MedicineResponseSchema, MedicineApiClient('http://127.0.0.1:8000')),
])
async def test_persistance(RequestSchema: type[MedicineModel | MedicineRequestSchema],
                           ResponseSchema: type[MedicineModel | MedicineResponseSchema],
                           mp: SupportsModelPersistance
                           ) -> None:
    assert RequestSchema in {MedicineModel, MedicineRequestSchema} and \
           ResponseSchema in {MedicineModel, MedicineResponseSchema}

    medicine: RequestSchema | ResponseSchema
    page: Page[ResponseSchema, MedicineFindQuery] | None

    requests: list[RequestSchema] = get_medicines(RequestSchema)

    responses: list[ResponseSchema] = []
    for i, medicine in enumerate(requests):
        stored_medicine: ResponseSchema | None = await mp.add(medicine)
        assert not stored_medicine is None
        assert not stored_medicine.id is None
        responses.append(stored_medicine)

    for medicine in responses:
        assert not medicine.id is None
        stored_medicine = await mp.find_by_id(medicine.id)
        assert stored_medicine is not None
        assert stored_medicine == medicine

    count: int = 0
    page: Page[ResponseSchema, MedicineFindQuery] | None = await mp.find(MedicineFindQuery(order_by=('created_at', 'desc')))
    assert page is not None
    while page:
        count += len(page.data)
        for i in range(1, len(page.data)):
            assert not page.data[i - 1].id is None and not page.data[i].id is None
            assert page.data[i - 1].created_at > page.data[i].created_at or (
                page.data[i - 1].created_at == page.data[i].created_at and
                page.data[i - 1].id > page.data[i].id
            )
        page = await mp.find(page.next)
    assert count == len(responses)

    medicine = responses[randint(0, len(responses) - 1)]
    assert not medicine.id is None
    medicine.description = "New description"
    stored_medicine = await mp.update(medicine.id, medicine)
    assert stored_medicine == medicine

    await mp.delete(medicine.id)
    assert await mp.find_by_id(medicine.id) is None
