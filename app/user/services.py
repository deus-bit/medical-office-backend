from app.user.repositories import AccountRepository, AccountFindQuery, ProfileRepository, ProfileFindQuery, RoleRepository, RoleFindQuery
from app.user.models import AccountModel, ProfileModel, RoleModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime
from typing import Optional
from app.user.schemas import UserRequestSchema

class AccountService(BaseService[AccountModel, AccountRepository, AccountFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.created_at

    async def get_email(self, id: Positive[int]) -> str:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.email

    async def get_enabled(self, id: Positive[int]) -> bool:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.enabled

    async def update_email(self, id: Positive[int], email: str) -> AccountModel:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        account.email = email
        return await self.repo.update(id, account)

    async def update_enabled(self, id: Positive[int], enabled: bool) -> AccountModel:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        account.enabled = enabled
        return await self.repo.update(id, account)

class ProfileService(BaseService[ProfileModel, ProfileRepository, ProfileFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.created_at

    async def get_name(self, id: Positive[int]) -> str:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.name

    async def update_name(self, id: Positive[int], name: str) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.name = name
        return await self.repo.update(id, profile)

class RoleService(BaseService[RoleModel, RoleRepository, RoleFindQuery]):
    async def get_created_at(self, id: Positive[int]) -> datetime:
        role: RoleModel | None = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.created_at

    async def get_name(self, id: Positive[int]) -> str:
        role: RoleModel | None = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.name

    async def update_name(self, id: Positive[int], name: str) -> RoleModel:
        role: RoleModel | None = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        role.name = name
        return await self.repo.update(id, role)

class UserService:
    def __init__(self, account_service: AccountService, profile_service: ProfileService, role_service: RoleService):
        self.account_service = account_service
        self.profile_service = profile_service
        self.role_service = role_service

    async def get_full_user(self, account_id: Positive[int]) -> Optional[dict]:
        account = await self.account_service.find_by_id(account_id)
        if not account:
            return None
        profile = await self.profile_service.find_by_id(account.profile_id)
        role = await self.role_service.find_by_id(account.role_id)
        return {
            'account': account,
            'profile': profile,
            'role': role
        }

    async def create_user(self, user_data: UserRequestSchema) -> dict:
        # Create profile
        profile = await self.profile_service.repo.add(ProfileModel.model_validate(user_data.profile))
        # Create or get role
        role = await self.role_service.repo.add(RoleModel.model_validate(user_data.role))
        # Create account with profile_id and role_id
        account_data = user_data.account.model_copy(update={
            'profile_id': profile.id,
            'role_id': role.id
        })
        account = await self.account_service.repo.add(AccountModel.model_validate(account_data))
        return {
            'account': account,
            'profile': profile,
            'role': role
        }
