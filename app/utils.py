# from fastapi import Path, Query, Header, Body
from typing import Annotated, Literal, Any, ClassVar, Self
from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, datetime
from pydantic import Field, BaseModel, BeforeValidator
from pydantic_core import CoreSchema, core_schema
import httpx
import re

# type InPath[T: Any] = Annotated[T, Path()]
# type InQuery[T: Any] = Annotated[T, Query()]
# type InHeader[T: Any] = Annotated[T, Header()]
# type InBody[T: Any] = Annotated[T, Body()]

type Number = int | float

type Positive[T: Number] = Annotated[T, Field(gt=0)]
type NonNegative[T: Number] = Annotated[T, Field(ge=0)]
type NonPositive[T: Number] = Annotated[T, Field(le=0)]
type Negative[T: Number] = Annotated[T, Field(lt=0)]

type OrderBy[T: Literal] = tuple[T, Literal['asc', 'desc']]

class RegEx(str):
    def __new__(cls, content: Any):
        if not isinstance(content, str):
            raise TypeError(f"Expected a string for regex pattern, got {type(content)}")
        try:
            re.compile(content)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: '{content}' - {e}")

        return super().__new__(cls, content)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            lambda v: cls(v),
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema()
        )

    def is_match(self, text: str) -> bool:
        return re.search(self, text) is not None

    def get_match_count(self, text: str) -> int:
        return len(re.findall(self, text))

    def find_all_matches(self, text: str) -> list[str]:
        return re.findall(self, text)

    def inject[S: Any](self, stmt: S, cls_attr, Any) -> S:
        return stmt


class Interval[T: Any](BaseModel):
    start: Annotated[T | None, Field(None)]
    end: Annotated[T | None, Field(None)]
    start_inclusive: Annotated[bool, Field(True)]
    end_inclusive: Annotated[bool, Field(False)]

    def inject[S: Any](self, stmt: S, cls_attr: Any) -> S:
        if not self.start is None:
            if self.start_inclusive:
                stmt = stmt.where(cls_attr >= self.start)
            else:
                stmt = stmt.where(cls_attr > self.start)
        if not self.end is None:
            if self.end_inclusive:
                stmt = stmt.where(cls_attr <= self.end)
            else:
                stmt = stmt.where(cls_attr < self.end)
        return stmt


class IntervalType(Enum):
    NUMBER = 'number'
    INT = 'int'
    FLOAT = 'float'
    DATE = 'date'
    DATETIME = 'datetime'


class _BaseIntervalMeta:
    _interval_type: ClassVar[IntervalType]

    @classmethod
    def _validate_interval_string_internal(cls, v: str, info: core_schema.ValidationInfo) -> str:
        interval_type = cls._interval_type

        match = re.match(r'^([\[\(])(.*?)\,(.*?)([\]\)])$', v)
        if not match:
            raise ValueError("Invalid interval string format.")

        start_closure, start_str, end_str, end_closure = match.groups()

        def parse_value(val_str: str) -> date | datetime | float | int:
            """Parses an interval endpoint string."""
            if val_str == 'inf':
                return float('inf')
            elif val_str == '-inf':
                return float('-inf')

            if interval_type == IntervalType.DATE:
                try: return date.fromisoformat(val_str)
                except ValueError: raise ValueError(f"Invalid date format: '{val_str}'. Expected YYYY-MM-DD.")
            elif interval_type == IntervalType.DATETIME:
                try: return datetime.fromisoformat(val_str)
                except ValueError: raise ValueError(f"Invalid datetime format: '{val_str}'. Expected YYYY-MM-DDTHH:MM:SS[.ffffff].")
            elif interval_type == IntervalType.INT:
                try: return int(val_str)
                except ValueError: raise ValueError(f"Invalid integer format: '{val_str}'. Expected a whole number.")
            elif interval_type == IntervalType.FLOAT or interval_type == IntervalType.NUMBER:
                try: return float(val_str)
                except ValueError: raise ValueError(f"Invalid number format: '{val_str}'. Expected a valid number (integer or float).")
            else:
                raise ValueError("Unsupported interval type for parsing (internal error).")

        start_val = parse_value(start_str)
        end_val = parse_value(end_str)

        if (start_str == 'inf' or start_str == '-inf') and start_closure == '[':
            raise ValueError(f"Interval starting with '{start_str}' must use an open bracket '('. Example: '({start_str},...'")

        if (end_str == 'inf' or end_str == '-inf') and end_closure == ']':
            raise ValueError(f"Interval ending with '{end_str}' must use an open bracket ')'. Example: '...,{end_str})'")

        def is_greater_than(a: Any, b: Any) -> bool:
            if a == float('inf'):
                return b != float('inf')
            elif b == float('-inf'):
                return a != float('-inf')
            elif a != float('-inf') and b != float('inf'):
                return a > b
            return False

        if is_greater_than(start_val, end_val):
            raise ValueError(f"Start value ({start_str}) must be less than or equal to end value ({end_str}).")

        return v

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> CoreSchema:
        str_schema = handler.generate_schema(str)

        return core_schema.with_info_after_validator_function(
            cls._validate_interval_string_internal,
            str_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda v: v)
        )


OPEN_BRACKET = r'[\[\(]'
CLOSE_BRACKET = r'[\]\)]'
INF = r'-?inf'

INTEGER = r'-?\d+'
FLOAT = r'-?\d+\.\d+'
NUMBER = rf'(?:{INTEGER}|{FLOAT})'

DATE = r'\d{4}-\d{2}-\d{2}'
TIME = r'\d{2}:\d{2}:\d{2}(?:\.\d+)?'
DATETIME = rf'{DATE}T{TIME}'

class NumberInterval(_BaseIntervalMeta, Annotated[str, Field(pattern=rf'^{OPEN_BRACKET}(?:{NUMBER}|{INF})\,(?:{NUMBER}|{INF}){CLOSE_BRACKET}$')]):
    _interval_type = IntervalType.NUMBER

class IntInterval(_BaseIntervalMeta, Annotated[str, Field(pattern=rf'^{OPEN_BRACKET}(?:{INTEGER}|{INF})\,(?:{INTEGER}|{INF}){CLOSE_BRACKET}$')]):
    _interval_type = IntervalType.INT

class FloatInterval(_BaseIntervalMeta, Annotated[str, Field(pattern=rf'^{OPEN_BRACKET}(?:{FLOAT}|{INF})\,(?:{FLOAT}|{INF}){CLOSE_BRACKET}$')]):
    _interval_type = IntervalType.FLOAT

class DateInterval(_BaseIntervalMeta, Annotated[str, Field(pattern=rf'^{OPEN_BRACKET}(?:{DATE}|{INF})\,(?:{DATE}|{INF}){CLOSE_BRACKET}$')]):
    _interval_type = IntervalType.DATE

class DatetimeInterval(_BaseIntervalMeta, Annotated[str, Field(pattern=rf'^{OPEN_BRACKET}(?:{DATETIME}|{INF})\,(?:{DATETIME}|{INF}){CLOSE_BRACKET}$')]):
    _interval_type = IntervalType.DATETIME


class HttpClient(ABC):
    @abstractmethod
    def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        ...

    @abstractmethod
    def post(self, url: str, data: dict | str | None = None, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        ...

    @abstractmethod
    def put(self, url: str, data: dict | str | None = None, headers: dict[str, str] | None = None) -> Any:
        ...

    @abstractmethod
    def delete(self, url: str, headers: dict[str, str] | None = None) -> Any:
        ...


class HttpxClient(HttpClient):
    def __init__(self, timeout: float = 3.0):
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)

    def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        response = self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, url: str, data: dict | str | None = None, json: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        response = self.client.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    def put(self, url: str, data: dict | str | None = None, headers: dict[str, str] | None = None) -> Any:
        response = self.client.put(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete(self, url: str, headers: dict[str, str] | None = None) -> Any:
        response = self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
