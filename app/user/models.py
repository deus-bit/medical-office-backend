from app.base.models import SQLModel, MappedColumn
from sqlmodel import Relationship
from typing import Literal, Annotated
from datetime import datetime, date

AccountAttribute = Literal['id', 'created_at', 'email', 'password', 'enabled', 'profile_id', 'role_id']

class AccountModel(SQLModel, table=True):
    __tablename__ = 'accounts'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    email: Annotated[str, MappedColumn(max_length=127)]
    password: Annotated[bytes, MappedColumn(max_length=32)]
    enabled: Annotated[bool, MappedColumn(True)]
    profile_id: Annotated[int, MappedColumn(gt=0, foreign_key="profiles.id", index=True)]
    role_id: Annotated[int, MappedColumn(gt=0, foreign_key="roles.id", index=True)]
    profile: Annotated['ProfileModel', Relationship(back_populates='accounts')]
    role: Annotated['RoleModel', Relationship(back_populates='accounts')]

ProfileAttribute = Literal['id', 'created_at', 'name', 'paternal', 'maternal', 'birthdate', 'phone']

class ProfileModel(SQLModel, table=True):
    __tablename__ = 'profiles'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=63)]
    paternal: Annotated[str, MappedColumn(max_length=31)]
    maternal: Annotated[str, MappedColumn(max_length=31)]
    phone: Annotated[int | None, MappedColumn(None, ge=60_000_000, lt=80_000_000, nullable=True)]
    birthdate: Annotated[date, MappedColumn()]


RoleAttribute = Literal['id', 'created_at', 'name']

class RoleModel(SQLModel, table=True):
    __tablename__ = 'roles'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=127, unique=True, index=True)]
