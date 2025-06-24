type Number = int | float
type Positive[T: Number] = Annotated[T, Field(gt=0)]
type OrderBy[T: Literal] = tuple[T, Literal['asc', 'desc']]

class FilterBy(TypedDict, total=False):
    ...


class FindQuery[F: FilterBy, A: Any](BaseModel):
    filter_by: Annotated[F, Field(default_factory=dict)]
    order_by: Annotated[OrderBy[A], Field()]
    last: Annotated[tuple[Positive[int]] | tuple[Positive[int], Any] | None, Field(None)]


class Page[T: Any, Q: FindQuery](BaseModel):
    next: Q
    data: list[T]


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


@pytest.mark.parametrize('RequestSchema,ResponseSchema,mp', [
    (MedicineModel, MedicineModel, InMemoryMedicineRepository()),
    (MedicineModel, MedicineModel, MedicineService(InMemoryMedicineRepository())),
    (MedicineRequestSchema, MedicineResponseSchema, MedicineApiClient('http://127.0.0.1:8080')),
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

