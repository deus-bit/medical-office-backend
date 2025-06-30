from app.user.repositories import AccountFindQuery, ProfileFindQuery, RoleFindQuery, UserFindQuery
from app.user.schemas import (
    AccountRequestSchema, AccountResponseSchema,
    ProfileRequestSchema, ProfileResponseSchema,
    RoleRequestSchema, RoleResponseSchema,
    UserRequestSchema, UserResponseSchema,
)
from app.exceptions import *
from app.utils import HttpClient, HttpxClient
from tests.integration.base import BaseApiClient
from datetime import datetime, date
import json

class AccountApiClient(BaseApiClient[AccountRequestSchema, AccountResponseSchema, AccountFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(AccountResponseSchema, host_url.rstrip('/') + '/v1/account', client)

    async def get_updated_at(self, id: int) -> datetime:
        account = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.updated_at

    async def get_email(self, id: int) -> str:
        account = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.email

    async def get_enabled(self, id: int) -> bool:
        account = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.enabled

    async def update_email(self, id: int, email: str) -> AccountResponseSchema:
        account = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        account.email = email
        return await self.update(id, account)

    async def update_enabled(self, id: int, enabled: bool) -> AccountResponseSchema:
        account = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        account.enabled = enabled
        return await self.update(id, account)


class ProfileApiClient(BaseApiClient[ProfileRequestSchema, ProfileResponseSchema, ProfileFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(ProfileResponseSchema, host_url.rstrip('/') + '/v1/profile', client)

    async def get_updated_at(self, id: int) -> datetime:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.updated_at

    async def get_name(self, id: int) -> str:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.name

    async def get_paternal(self, id: int) -> str:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.paternal

    async def get_maternal(self, id: int) -> str:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.maternal

    async def get_phone(self, id: int) -> int | None:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.phone

    async def get_birthdate(self, id: int) -> date:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.birthdate

    async def update_name(self, id: int, name: str) -> ProfileResponseSchema:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.name = name
        return await self.update(id, profile)

    async def update_paternal(self, id: int, paternal: str) -> ProfileResponseSchema:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.paternal = paternal
        return await self.update(id, profile)

    async def update_maternal(self, id: int, maternal: str) -> ProfileResponseSchema:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.maternal = maternal
        return await self.update(id, profile)

    async def update_phone(self, id: int, phone: int | None) -> ProfileResponseSchema:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.phone = phone
        return await self.update(id, profile)

    async def update_birthdate(self, id: int, birthdate: date) -> ProfileResponseSchema:
        profile = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.birthdate = birthdate
        return await self.update(id, profile)


class RoleApiClient(BaseApiClient[RoleRequestSchema, RoleResponseSchema, RoleFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(RoleResponseSchema, host_url.rstrip('/') + '/v1/role', client)

    async def get_created_at(self, id: int) -> datetime:
        role = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.created_at

    async def get_updated_at(self, id: int) -> datetime:
        role = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.updated_at

    async def get_name(self, id: int) -> str:
        role = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.name

    async def update_name(self, id: int, name: str) -> RoleResponseSchema:
        role = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        role.name = name
        return await self.update(id, role)

    async def find_by_name(self, name: str) -> RoleResponseSchema | None:
        # Simulate a find by name using find
        page = await self.find(RoleFindQuery(filter_by={'name': name}, order_by=('id', 'asc')))
        if page and page.data:
            role = page.data[0]
            if isinstance(role, RoleResponseSchema):
                return role
            return RoleResponseSchema(**role.model_dump())
        return None

    async def get_users(self, id: int) -> list[UserResponseSchema]:
        role = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        # This would require a user client or endpoint to fetch users by role
        raise NotImplementedError("Fetching users by role is not implemented in this client.")


class UserApiClient(BaseApiClient[UserRequestSchema, UserResponseSchema, UserFindQuery]):
    def __init__(self, host_url: str, client: HttpClient = HttpxClient()) -> None:
        super().__init__(UserResponseSchema, host_url.rstrip('/') + '/v1/user', client)

    async def get_created_at(self, id: int) -> datetime:
        user = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.created_at

    async def get_role(self, id: int) -> RoleResponseSchema:
        user = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.role

    async def update_role_by_name(self, id: int, role_name: str) -> UserResponseSchema:
        url = f"{self.base_route}/{id}/role"
        response = self.client.put(url, data=json.dumps(role_name), headers={"Content-Type": "application/json"})
        return self.ResponseSchema(**response)

    async def get_account(self, id: int) -> AccountResponseSchema:
        user = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.account

    async def get_profile(self, id: int) -> ProfileResponseSchema:
        user = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.profile
