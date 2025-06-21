from typing import Literal, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime, date

AccountAttribute = Literal['id', 'created_at', 'email', 'password', 'enabled', 'profile_id', 'role_id']

class AccountModel(SQLModel, table=True):
    __tablename__ = 'accounts'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    email: Annotated[str, Field(max_length=127)]
    password: Annotated[bytes, Field(max_length=32)]
    enabled: Annotated[bool, Field(True)]
    profile_id: Annotated[int, Field(gt=0, foreign_key="profiles.id", index=True)]
    role_id: Annotated[int, Field(gt=0, foreign_key="roles.id", index=True)]


ProfileAttribute = Literal['id', 'created_at', 'name', 'paternal', 'maternal', 'birthdate', 'phone']

class ProfileModel(SQLModel, table=True):
    __tablename__ = 'profiles'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    name: Annotated[str, Field(max_length=63)]
    paternal: Annotated[str, Field(max_length=31)]
    maternal: Annotated[str, Field(max_length=31)]
    phone: Annotated[int | None, Field(None, ge=60_000_000, lt=80_000_000, nullable=True)]
    birthdate: Annotated[date, Field()]


RoleAttribute = Literal['id', 'created_at', 'name']

class RoleModel(SQLModel, table=True):
    __tablename__ = 'roles'

    id: Annotated[int | None, Field(None, gt=0, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    name: Annotated[str, Field(max_length=127, unique=True, index=True)]
