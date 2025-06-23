from app.base.models import Page, FindQuery
from app.exceptions import *
from app.utils import HttpxClient, HttpClient, Positive
from pydantic import BaseModel
from typing import Any
from abc import ABC
import httpx

class BaseApiClient[RequestSchema: BaseModel, ResponseSchema: BaseModel, Query: FindQuery](ABC):
    def __init__(self, _ResponseSchema: type[ResponseSchema],
                 base_route: str,
                 client: HttpClient = HttpxClient()
                 ) -> None:
        self.base_route = base_route.rstrip('/')
        self.ResponseSchema = _ResponseSchema
        self.client = client

    async def add(self, model: RequestSchema) -> ResponseSchema:
        url: str = f"{self.base_route}"
        response: dict[str, Any] = self.client.post(url, json=model.model_dump(mode='json'))
        return self.ResponseSchema(**response)

    async def find(self, query: Query) -> Page[RequestSchema, Query] | None:
        url: str = f"{self.base_route}/find"
        response: dict[str, Any] = self.client.post(url, json=query.model_dump(mode='json'))
        if not response:
            return None
        response["data"] = [self.ResponseSchema(**model) for model in response.get("data", [])]
        return Page[RequestSchema, Query](**response)

    async def find_by_id(self, id: Positive[int]) -> ResponseSchema | None:
        url: str = f"{self.base_route}/{id}"
        try:
            response: dict[str, Any] = self.client.get(url)
            return self.ResponseSchema(**response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise e

    async def update(self, id: Positive[int], model: RequestSchema) -> ResponseSchema:
        url: str = f"{self.base_route}/{id}"
        response: dict[str, Any] = self.client.put(url, json=model.model_dump(mode='json'))
        return self.ResponseSchema(**response)

    async def delete(self, id: Positive[int]) -> ResponseSchema:
        url: str = f"{self.base_route}/{id}"
        response: dict[str, Any] = self.client.delete(url)
        return self.ResponseSchema(**response)
