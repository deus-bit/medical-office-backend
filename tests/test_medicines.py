from app.medicine.repositories import (
    MedicineFindQuery,
    SupabaseMedicineRepository,
)
from app.medicine.services import MedicineService
from app.medicine.schemas import MedicineRequestSchema, MedicineResponseSchema
from app.medicine.models import MedicineModel
from app.base.common import SupportsModelPersistance
from app.base.models import Page
from tests.integration.medicine import MedicineApiClient
from random import randint
import pytest

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

@pytest.mark.parametrize('request_schema,response_schema,mp', [
    (MedicineModel, MedicineModel, SupabaseMedicineRepository()),
    (MedicineModel, MedicineModel, MedicineService(SupabaseMedicineRepository())),
    # (MedicineRequestSchema, MedicineResponseSchema, MedicineApiClient('http://127.0.0.1:8080')),
])
async def test_basic_persistance(request_schema: type[MedicineModel | MedicineRequestSchema],
                                 response_schema: type[MedicineModel | MedicineResponseSchema],
                                 mp: SupportsModelPersistance
                                 ) -> None:
    assert request_schema in {MedicineModel, MedicineRequestSchema} and \
           response_schema in {MedicineModel, MedicineResponseSchema}

    medicine: request_schema | response_schema
    page: Page[response_schema, MedicineFindQuery] | None

    requests: list[request_schema] = get_medicines(request_schema)

    responses: list[response_schema] = []
    for medicine in requests:
        persisted_medicine: response_schema | None = await mp.add(medicine)
        assert persisted_medicine is not None
        assert persisted_medicine.id is not None
        responses.append(persisted_medicine)

    for medicine in responses:
        assert medicine.id is not None
        persisted_medicine = await mp.find_by_id(medicine.id)
        assert persisted_medicine is not None
        assert persisted_medicine == medicine

    count: int = 0
    page: Page[response_schema, MedicineFindQuery] | None = await mp.find(MedicineFindQuery(order_by=('created_at', 'desc')))
    assert page is not None
    while page:
        count += len(page.data)
        for i in range(1, len(page.data)):
            assert page.data[i - 1].id and page.data[i].id
            assert page.data[i - 1].created_at > page.data[i].created_at or (
                page.data[i - 1].created_at == page.data[i].created_at and
                page.data[i - 1].id > page.data[i].id
            )
        page = await mp.find(page.next)
    assert (count - 1) % (len(responses) - 1) == 0

    medicine = responses[randint(0, len(responses) - 1)]
    assert medicine.id is not None
    medicine.description = "New description"
    persisted_medicine = await mp.update(medicine.id, medicine)
    assert persisted_medicine == medicine

    await mp.delete(medicine.id)
    assert await mp.find_by_id(medicine.id) is None
