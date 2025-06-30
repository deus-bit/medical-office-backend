from sqlmodel.sql._expression_select_cls import SelectOfScalar
from app.base.models import BaseModel, SQLModel, FindQuery, Page
from app.base.common import SupportsModelPersistance
from app.exceptions import *
from app.utils import Positive
from sqlalchemy import Engine, exc, text
from sqlmodel import Session, select
from typing import override
from collections.abc import Generator

class BaseRepository[Model: BaseModel, Query: FindQuery](SupportsModelPersistance[Model, Query]):
    ...


class SQLRepository[Model: SQLModel, Query: FindQuery](BaseRepository):
    def __init__(self, model: type[Model], engine: Engine, page_size_max: Positive[int]) -> None:
        self.engine = engine
        self.page_size_max = page_size_max
        self.model = model

        self.model.__table__.create(engine, checkfirst=True)

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
        existing = await self.find_by_id(id)
        if not existing:
            raise EntityNotFound()
        for field, value in model.model_dump(exclude={'id', 'created_at', 'updated_at'}, exclude_unset=True).items():
            setattr(existing, field, value)
        return await self.upsert(existing)

    @override
    async def delete(self, id: Positive[int]) -> Model:
        stored_model = await self.find_by_id(id)
        if stored_model:
            proc = self._proc_name('Delete')
            with self.engine.connect() as conn:
                result = conn.execute(text(f"CALL {proc}(:id)"), {'id': id})
                row = result.mappings().fetchone()
                if not row:
                    raise EntityNotFound()
                return self.model(**row)
        raise EntityNotFound()

    @override
    async def upsert(self, model: Model) -> Model:
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model


class ProcSQLRepository[Model: SQLModel, Query: FindQuery](BaseRepository):
    def __init__(self, model: type[Model], engine: Engine, page_size_max: Positive[int]):
        self.engine = engine
        self.model = model
        self.page_size_max = page_size_max

    def _proc_name(self, verb: str) -> str:
        return f"{verb}{self.model.__name__}"

    @override
    async def add(self, model: Model) -> Model:
        if model.id:
            raise EntityAlreadyExists()
        
        proc = self._proc_name('Create')
        # Extract model data excluding id
        model_data = model.model_dump(exclude={'id'})
        
        # Build parameter list dynamically
        param_names = [f"p_{field}" for field in model_data.keys()]
        param_placeholders = [f":{param}" for param in param_names]
        
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}({', '.join(param_placeholders)})"), model_data)
            row = result.mappings().fetchone()
            if not row:
                raise EntityNotFound()
            return self.model(**row)

    @override
    async def update(self, id: Positive[int], model: Model) -> Model:
        proc = self._proc_name('Update')
        # Extract model data excluding id, created_at, updated_at
        model_data = model.model_dump(exclude={'id', 'created_at', 'updated_at'}, exclude_unset=True)
        model_data['p_id'] = id
        
        # Build parameter list dynamically
        param_names = ['p_id'] + [f"p_{field}" for field in model.model_dump(exclude={'id'}).keys()]
        param_placeholders = [f":{param}" for param in param_names]
        
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}({', '.join(param_placeholders)})"), model_data)
            row = result.mappings().fetchone()
            if not row:
                raise EntityNotFound()
            return self.model(**row)

    @override
    async def delete(self, id: Positive[int]) -> Model:
        proc = self._proc_name('Delete')
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}(:p_id)"), {'p_id': id})
            row = result.mappings().fetchone()
            if not row:
                raise EntityNotFound()
            return self.model(**row)

    @override
    async def upsert(self, model: Model) -> Model:
        proc = self._proc_name('Upsert')
        # Extract model data including id
        model_data = model.model_dump()
        
        # Build parameter list dynamically
        param_names = [f"p_{field}" for field in model_data.keys()]
        param_placeholders = [f":{param}" for param in param_names]
        
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}({', '.join(param_placeholders)})"), model_data)
            row = result.mappings().fetchone()
            if not row:
                raise EntityNotFound()
            return self.model(**row)

    @override
    async def find_by_id(self, id: Positive[int]) -> Model | None:
        proc = self._proc_name('FindOne')
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}(:p_id)"), {'p_id': id})
            row = result.mappings().fetchone()
            return self.model(**row) if row else None

    @override
    async def find(self, query: Query) -> Page[Model, Query] | None:
        proc = self._proc_name('Find')
        
        # Extract order_by and last from query
        order_by_column, order_by_direction = query.order_by
        last_id = None
        last_value = None
        
        if query.last:
            if len(query.last) == 1:
                last_id = query.last[0]
            elif len(query.last) == 2:
                last_id, last_value = query.last

        params = {
            'p_order_by_column': order_by_column,
            'p_order_by_direction': order_by_direction,
            'p_last_id': last_id,
            'p_last_value': last_value,
            'p_limit': self.page_size_max
        }
        
        with self.engine.connect() as conn:
            result = conn.execute(text(f"CALL {proc}(:p_order_by_column, :p_order_by_direction, :p_last_id, :p_last_value, :p_limit)"), params)
            rows = result.mappings().fetchall()
            models = [self.model(**row) for row in rows]
            
            if not models:
                return None
            
            if order_by_column != 'id':
                query.last = models[-1].id, getattr(models[-1], order_by_column)
            else:
                query.last = (models[-1].id,)
            
            return Page[Model, Query](
                next=query,
                data=models,
            )
