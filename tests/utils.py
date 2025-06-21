from app.generics import Page, FindQuery
from app.utils import HttpxClient, HttpClient, Positive
from pydantic import BaseModel

class HttpClientService[Model: BaseModel, Query: FindQuery]:
    def __init__(self, model: type[Model], base_route: str, client: HttpClient = HttpxClient()):
        self.base_route = base_route.rstrip('/')
        self.model = model
        self.client = client

    async def add(self, model: Model) -> Model:
        url = f"{self.base_route}"
        response = self.client.post(url, json=model.model_dump_json())
        return self.model(**response)

    async def find(self, query: Query) -> Page[Model, Query] | None:
        url = f"{self.base_route}/find"
        response = self.client.post(url, json=query.model_dump_json())
        if not response:
            return None
        response["data"] = [self.model(**model) for model in response.get("data", [])]
        return Page[Model, Query](**response)

    async def find_by_id(self, id: Positive[int]) -> Model | None:
        url = f"{self.base_route}/{id}"
        try:
            response = self.client.get(url)
            return self.model(**response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"Item with ID {id} not found.")
                return None

    async def update(self, id: Positive[int], model: Model) -> Model:
        url = f"{self.base_route}/{id}"
        response = self.client.put(url, json=model.model_dump_json())
        return self.model(**response)

    async def delete(self, id: Positive[int]) -> Model:
        url = f"{self.base_route}/{id}"
        response = self.client.delete(url)
        return self.model(**response)
