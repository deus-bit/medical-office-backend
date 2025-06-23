# class ExampleRouter(APIRouter):
#     def __init__(self, prefix: str, service_factory: Callable[[], Service]) -> None:
#         super().__init__(prefix=prefix)
#         self.svc = service_factory

#         self.add_api_route('/', self.post_medicine, name="Post Item", methods=['post'])
#         self.add_api_route('/find', self.find_medicines, name="Find Items", methods=['post'])

#         self.add_api_route('/{id}', self.get_medicine, name="Get Item", methods=['get'])
#         self.add_api_route('/{id}', self.put_medicine, name="Put Item", methods=['put'])
#         self.add_api_route('/{id}', self.delete_medicine, name="Delete Item", methods=['delete'])


# class HttpxClientService[Model: BaseModel, Query: FindQuery]:
#     def __init__(self, model: type[Model], base_route: str, client: HttpClient = HttpxClient()):
#         self.base_route = base_route.rstrip('/')
#         self.model = model
#         self.client = client

#     async def add(self, model: Model) -> Model:
#         url = f"{self.base_route}"
#         response = self.client.post(url, json=model.model_dump())
#         return self.model(**response)

#     async def find(self, query: Query) -> Optional[Page[Model, Query]]:
#         url = f"{self.base_route}/find"
#         response = self.client.post(url, json=query.model_dump())
#         response["data"] = [self.model(**model) for model in response.get("data", [])]
#         return Page[Model, Query](**response)

#     async def find_by_id(self, id: Positive[int]) -> Optional[Model]:
#         url = f"{self.base_route}/{id}"
#         try:
#             response = self.client.get(url)
#             return self.model(**response)
#         except httpx.HTTPStatusError as e:
#             if e.response.status_code == 404:
#                 print(f"Item with ID {id} not found.")
#                 return None

#     async def update(self, id: Positive[int], model: Model) -> Model:
#         url = f"{self.base_route}/{id}"
#         response = self.client.put(url, json=model.model_dump())
#         return self.model(**response)

#     async def delete(self, id: Positive[int]) -> Model:
#         url = f"{self.base_route}/{id}"
#         response = self.client.delete(url)
#         return self.model(**response)
