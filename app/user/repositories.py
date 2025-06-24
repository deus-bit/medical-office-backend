from app.user.models import (
    AccountModel, AccountAttribute,
    ProfileModel, ProfileAttribute,
    RoleModel, RoleAttribute,
    UserModel, UserAttribute,
)
from app.exceptions import *
from app.base.repositories import BaseRepository, SQLRepository
from app.base.models import FindQuery, FilterBy
from app.config import settings
from app.utils import Interval, RegEx, Number
from sqlmodel import create_engine, select
from datetime import datetime, date
from typing import override
from abc import ABC, abstractmethod

class AccountFilterBy(FilterBy, total=False):
    id: Interval[Number]
    updated_at: Interval[datetime]
    email: RegEx
    enabled: bool


class AccountFindQuery(FindQuery[AccountFilterBy, AccountAttribute]):
    ...


class AccountRepository(BaseRepository[AccountModel, AccountFindQuery], ABC):
    ...


class InMemoryAccountRepository(SQLRepository[AccountModel, AccountFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=AccountModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseAccountRepository(SQLRepository[AccountModel, AccountFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=AccountModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )


class ProfileFilterBy(FilterBy, total=False):
    id: Interval[int]
    updated_at: Interval[datetime]
    name: RegEx
    paternal: RegEx
    maternal: RegEx
    birthdate: Interval[date]
    phone: Interval[int]


class ProfileFindQuery(FindQuery[ProfileFilterBy, ProfileAttribute]):
    ...


class ProfileRepository(BaseRepository[ProfileModel, ProfileFindQuery], ABC):
    ...


class InMemoryProfileRepository(SQLRepository[ProfileModel, ProfileFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ProfileModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseProfileRepository(SQLRepository[ProfileModel, ProfileFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=ProfileModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )


class RoleFilterBy(FilterBy, total=False):
    id: Interval[int]
    created_at: Interval[datetime]
    updated_at: Interval[datetime]
    name: RegEx


class RoleFindQuery(FindQuery[RoleFilterBy, RoleAttribute]):
    ...


class RoleRepository(BaseRepository[RoleModel, RoleFindQuery], ABC):
    @abstractmethod
    async def find_by_name(self, name: str) -> RoleModel | None: ...


class RoleSQLRepository(SQLRepository[RoleModel, RoleFindQuery], RoleRepository):
    async def create_defaults(self) -> None:
        roles = ["Base User", "Family Medicine Doctor", "Administrator"]
        for role in roles:
            if not await self.find_by_name(role):
                await self.add(RoleModel(name=role))

    async def find_by_name(self, name: str) -> RoleModel | None:
        assert isinstance(name, str), "Name must be a string."
        return self.session.exec(select(self.model).where(getattr(self.model, 'name') == name)).first()


class InMemoryRoleRepository(RoleSQLRepository):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=RoleModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseRoleRepository(RoleSQLRepository):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=RoleModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )


class UserFilterBy(FilterBy, total=False):
    id: Interval[int]
    created_at: Interval[datetime]
    account_id: Interval[int]
    profile_id: Interval[int]
    role_id: Interval[int]


class UserFindQuery(FindQuery[UserFilterBy, UserAttribute]):
    ...


class UserRepository(BaseRepository[UserModel, UserFindQuery], ABC):
    ...


class InMemoryUserRepository(SQLRepository[UserModel, UserFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=UserModel,
            engine=create_engine(url="sqlite://", connect_args={
                'timeout': 2.0,
                'cached_statements': 512
            }),
            page_size_max=64
        )


class SupabaseUserRepository(SQLRepository[UserModel, UserFindQuery]):
    @override
    def __init__(self) -> None:
        super().__init__(
            model=UserModel,
            engine=create_engine(url=settings.supabase_url),
            page_size_max=64
        )
