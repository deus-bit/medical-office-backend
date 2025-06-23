from app.base.repositories import BaseRepository, FindQuery
from app.base.models import BaseModel
from app.base.models import Page
from app.utils import Positive
from abc import ABC

class BaseService[Model: BaseModel, Repository: BaseRepository, Query: FindQuery](ABC):
    def __init__(self, repository: Repository) -> None:
        self.repo = repository

    async def add(self, model: Model) -> Model:
        return await self.repo.add(model)

    async def find(self, query: FindQuery) -> Page[Model, Query] | None:
        return await self.repo.find(query)

    async def find_by_id(self, id: Positive[int]) -> Model | None:
        return await self.repo.find_by_id(id)

    async def update(self, id: Positive[int], model: Model) -> Model:
        return await self.repo.update(id, model)

    async def delete(self, id: Positive[int]) -> Model:
        return await self.repo.delete(id)

    async def upsert(self, model: Model) -> Model:
        return await self.repo.upsert(model)
