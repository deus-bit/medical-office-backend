from app.base.models import SQLModel, MappedColumn
from sqlmodel import Relationship
from typing import Literal, Annotated
from datetime import datetime, date

AccountAttribute = Literal['id', 'updated_at', 'email', 'password', 'enabled']

class AccountModel(SQLModel, table=True):
    __tablename__ = 'accounts'

    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    email: Annotated[str, MappedColumn(max_length=127)]
    password: Annotated[bytes, MappedColumn(max_length=32)]
    enabled: Annotated[bool, MappedColumn(True)]


ProfileAttribute = Literal['id', 'updated_at', 'name', 'paternal', 'maternal', 'birthdate', 'phone']

class ProfileModel(SQLModel, table=True):
    __tablename__ = 'profiles'

    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=63)]
    paternal: Annotated[str, MappedColumn(max_length=31)]
    maternal: Annotated[str, MappedColumn(max_length=31)]
    phone: Annotated[int | None, MappedColumn(None, ge=60_000_000, lt=80_000_000, nullable=True)]
    birthdate: Annotated[date, MappedColumn()]


RoleAttribute = Literal['id', 'created_at', 'updated_at', 'name']

class RoleModel(SQLModel, table=True):
    __tablename__ = 'roles'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=127, unique=True, index=True)]


UserAttribute = Literal['id', 'account_id', 'profile_id', 'role_id']

class UserModel(SQLModel, table=True):
    __tablename__ = 'users'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    account_id: Annotated[int, MappedColumn(gt=0, foreign_key="accounts.id", unique=True)]
    profile_id: Annotated[int, MappedColumn(gt=0, foreign_key="profiles.id", unique=True)]
    role_id: Annotated[int, MappedColumn(gt=0, foreign_key="roles.id", unique=True)]

    account: Annotated[AccountModel, Relationship(sa_relationship_kwargs={"uselist": False})]
    profile: Annotated[ProfileModel, Relationship(sa_relationship_kwargs={"uselist": False})]
    role: Annotated[RoleModel, Relationship(sa_relationship_kwargs={"uselist": False})]
