from app.exceptions import *
from app.utils import Positive, OrderBy, Interval, RegEx
from sqlalchemy import Engine, exc
from sqlmodel import SQLModel, Session, select
from pydantic import BaseModel, Field
from typing import Annotated, Any, TypedDict, Self, override
from abc import ABC, abstractmethod

class FilterBy(TypedDict, total=False):
    ...


class FindQuery[T: Any, F: FilterBy, A: Any](BaseModel):
    filter_by: Annotated[F, Field(default_factory=dict)]
    order_by: Annotated[OrderBy[A], Field()]
    last: Annotated[T | None, Field(None)]


class Page[T: Any, Q: FindQuery](BaseModel):
    next: Q
    data: list[T]


class BaseRepository[Model: BaseModel, Query: FindQuery](ABC):
    @abstractmethod
    async def add(self, model: Model) -> Model: ...

    @abstractmethod
    async def find(self, query: Query) -> Page[Model, Query] | None: ...

    @abstractmethod
    async def find_by_id(self, id: Positive[int]) -> Model | None: ...

    @abstractmethod
    async def update(self, id: Positive[int], model: Model) -> Model: ...

    @abstractmethod
    async def delete(self, id: Positive[int]) -> Model: ...

    @abstractmethod
    async def upsert(self, model: Model) -> Model: ...


class SQLRepository[Model: SQLModel, Query: FindQuery](BaseRepository):
    def __init__(self, model: type[Model], engine: Engine, page_size_max: Positive[int]) -> None:
        self.engine = engine
        self.page_size_max = page_size_max
        self.model = model

        self.model.__table__.create(engine)

        self.session_generator = self.get_session_generator()
        self.session = next(self.session_generator)

    def get_session_generator(self) -> Session:
        try:
            session = Session(self.engine)
            yield session
        except exc.TimeoutError:
            raise ConnectionTimeout()
        except Exception:
            session.rollback()
        finally:
            session.close()

    @override
    async def add(self, model: Model) -> Model:
        if model.id:
            raise EntityAlreadyExists()
        return await self.upsert(model)

    @override
    async def find_by_id(self, id: Positive[int]) -> Model | None:
        return self.session.get(self.model, id)

    @override
    async def find(self, query: Query) -> Page[Model, Query] | None:
        assert isinstance(query, FindQuery), "Invalid query type."
        filter_by, order_by, last_retrieved = query.filter_by, query.order_by, query.last
        stmt = select(self.model).limit(self.page_size_max)

        for attr, f_value in filter_by.items():
            stmt = f_value.inject(stmt, getattr(self.model, attr))

        if last_retrieved:
            if order_by[1] == 'asc':
                if order_by[0] != 'id':
                    stmt = stmt.where(
                        (getattr(self.model, order_by[0]) > getattr(last_retrieved, order_by[0])) |
                        ((getattr(self.model, order_by[0]) == getattr(last_retrieved, order_by[0])) &
                            (self.model.id > last_retrieved.id))
                    )
                else:
                    stmt = stmt.where(self.model.id > last_retrieved.id)
            else:
                if order_by[0] != 'id':
                    stmt = stmt.where(
                        (getattr(self.model, order_by[0]) < getattr(last_retrieved, order_by[0])) |
                        ((getattr(self.model, order_by[0]) == getattr(last_retrieved, order_by[0])) &
                            (self.model.id < last_retrieved.id))
                    )
                else:
                    stmt = stmt.where(self.model.id < last_retrieved.id)

        for attr in [order_by[0], 'id'] if order_by[0] != 'id' else ['id']:
            stmt = stmt.order_by(getattr(getattr(self.model, attr), order_by[1])())

        models: list[Model] = self.session.exec(stmt).all()

        if not models:
            return None

        query.last = models[-1]

        return Page[Model, Query](
            next=query,
            data=models,
        )

    @override
    async def update(self, id: Positive[int], model: Model) -> Model:
        if self.session.get_one(self.model, id):
            model.id = id
            return await self.upsert(model)
        raise EntityNotFound()

    @override
    async def delete(self, id: Positive[int]) -> Model:
        if stored_model := self.session.get_one(self.model, id):
            self.session.delete(stored_model)
            self.session.commit()
            return stored_model
        raise EntityNotFound()

    @override
    async def upsert(self, model: Model) -> Model:
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model
