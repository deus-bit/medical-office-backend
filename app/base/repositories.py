from sqlmodel.sql._expression_select_cls import SelectOfScalar
from app.base.models import BaseModel, SQLModel, FindQuery, Page
from app.base.common import SupportsModelPersistance
from app.exceptions import *
from app.utils import Positive
from sqlalchemy import Engine, exc
from sqlmodel import Session, select
from typing import override
from collections.abc import Generator
from datetime import datetime
from app.utils import parse_last_retrieved

class BaseRepository[Model: BaseModel, Query: FindQuery](SupportsModelPersistance[Model, Query]):
    ...


class SQLRepository[Model: SQLModel, Query: FindQuery](BaseRepository):
    def __init__(self, model: type[Model], engine: Engine, page_size_max: Positive[int]) -> None:
        self.engine = engine
        self.page_size_max = page_size_max
        self.model = model

        self.model.__table__.create(engine)

        self.session_generator = self.get_session_generator()
        self.session = next(self.session_generator)

    def get_session_generator(self) -> Generator[Session]:
        session: Session = Session(self.engine)
        try:
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
        stmt: SelectOfScalar[type[Model]] = select(self.model).limit(self.page_size_max)

        for attr, f_value in filter_by.items():
            stmt = f_value.inject(stmt, getattr(self.model, attr))

        if last_retrieved:
            if order_by[1] == 'asc':
                if order_by[0] != 'id' and len(last_retrieved) == 2:
                    stmt = stmt.where(
                        (getattr(self.model, order_by[0]) > last_retrieved[1]) |
                        ((getattr(self.model, order_by[0]) == last_retrieved[1]) &
                            (self.model.id > last_retrieved[0]))
                    )
                elif len(last_retrieved) == 1:
                    stmt = stmt.where(self.model.id > last_retrieved[0])
            else:
                if order_by[0] != 'id':
                    stmt = stmt.where(
                        (getattr(self.model, order_by[0]) < last_retrieved[1]) |
                        ((getattr(self.model, order_by[0]) == last_retrieved[1]) &
                            (self.model.id < last_retrieved[0]))
                    )
                elif len(last_retrieved) == 1:
                    stmt = stmt.where(self.model.id < last_retrieved[0])

        for attr in [order_by[0], 'id'] if order_by[0] != 'id' else ['id']:
            stmt = stmt.order_by(getattr(getattr(self.model, attr), order_by[1])())

        models: list[Model] = self.session.exec(stmt).all()

        if not models:
            return None

        if order_by[0] != 'id':
            query.last = models[-1].id, getattr(models[-1], order_by[0])
        else:
            query.last = models[-1].id,

        return Page[Model, Query](
            next=query,
            data=models,
        )

    @override
    async def update(self, id: Positive[int], model: Model) -> Model:
        existing = self.session.get(self.model, id)
        if not existing:
            raise EntityNotFound()
        for field, value in model.model_dump(exclude={'id', 'created_at', 'updated_at'}, exclude_unset=True).items():
            setattr(existing, field, value)
        return await self.upsert(existing)

    @override
    async def delete(self, id: Positive[int]) -> Model:
        stored_model: Model | None = self.session.get(self.model, id)
        if stored_model:
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
