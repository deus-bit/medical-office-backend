from __future__ import annotations
from app.base.models import SQLModel, MappedColumn
from sqlmodel import Relationship
from typing import Literal, Annotated
from datetime import datetime, date

AccountAttribute = Literal['id', 'updated_at', 'email', 'password', 'enabled']

class AccountModel(SQLModel, table=True):
    __tablename__ = 'accounts'

    id: Annotated[int | None, MappedColumn(None, gt=0, primary_key=True, foreign_key="users.id")]
    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    email: Annotated[str, MappedColumn(max_length=127)]
    password: Annotated[bytes, MappedColumn(max_length=32)]
    enabled: Annotated[bool, MappedColumn(True)]

    user: UserModel = Relationship(back_populates="account")


ProfileAttribute = Literal['id', 'updated_at', 'name', 'paternal', 'maternal', 'birthdate', 'phone']

class ProfileModel(SQLModel, table=True):
    __tablename__ = 'profiles'

    id: Annotated[int | None, MappedColumn(None, gt=0, primary_key=True, foreign_key="users.id")]
    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn(max_length=63)]
    paternal: Annotated[str, MappedColumn(max_length=31)]
    maternal: Annotated[str, MappedColumn(max_length=31)]
    phone: Annotated[int | None, MappedColumn(None, ge=60_000_000, lt=80_000_000, nullable=True)]
    birthdate: Annotated[date, MappedColumn()]

    user: UserModel = Relationship(back_populates="profile")


RoleAttribute = Literal['id', 'created_at', 'updated_at', 'name']

class RoleModel(SQLModel, table=True):
    __tablename__ = 'roles'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    updated_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    name: Annotated[str, MappedColumn('Base User', max_length=127, unique=True, index=True)]

    users: UserModel = Relationship(back_populates="role")


UserAttribute = Literal['id', 'created_at', 'role_id']

class UserModel(SQLModel, table=True):
    __tablename__ = 'users'

    created_at: Annotated[datetime, MappedColumn(default_factory=datetime.now)]
    role_id: Annotated[int | None, MappedColumn(None, gt=0, foreign_key="roles.id")]

    role: RoleModel = Relationship(back_populates="users")
    account: AccountModel = Relationship(back_populates="user")
    profile: ProfileModel = Relationship(back_populates="user")
