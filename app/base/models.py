from app.exceptions import *
from app.utils import OrderBy, Positive
from sqlmodel import SQLModel as _SQLModel, Field as MappedColumn
from pydantic import BaseModel as _BaseModel, ConfigDict, Field
from typing import Any, Annotated, TypedDict, ClassVar

class BaseModel(_BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class SQLModel(_SQLModel, BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: Annotated[int | None, MappedColumn(None, gt=0, primary_key=True)]


class FilterBy(TypedDict, total=False):
    ...


class FindQuery[F: FilterBy, A: Any](BaseModel):
    filter_by: Annotated[F, Field(default_factory=dict)]
    order_by: Annotated[OrderBy[A], Field()]
    last: Annotated[tuple[Positive[int]] | tuple[Positive[int], Any] | None, Field(None)]


class Page[T: Any, Q: FindQuery](BaseModel):
    next: Q
    data: list[T]
