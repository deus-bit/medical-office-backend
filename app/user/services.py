from app.user.repositories import AccountRepository, AccountFindQuery, ProfileRepository, ProfileFindQuery, RoleRepository, RoleFindQuery, UserRepository, UserFindQuery
from app.user.models import AccountModel, ProfileModel, RoleModel, UserModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime
from typing import Optional, override

class AccountService(BaseService[AccountModel, AccountRepository, AccountFindQuery]):
    async def get_updated_at(self, id: Positive[int]) -> datetime:
        account: AccountModel | None = await self.find_by_id(id)
        if not account:
            raise EntityNotFound()
        return account.updated_at

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
    async def get_updated_at(self, id: Positive[int]) -> datetime:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.updated_at

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

    async def get_updated_at(self, id: Positive[int]) -> datetime:
        role: RoleModel | None = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.updated_at

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
    
    async def find_by_name(self, name: str) -> Optional[RoleModel]:
        return await self.repo.find_by_name(name)


class UserService(BaseService[UserModel, UserRepository, UserFindQuery]):
    def __init__(self, repository: UserRepository,
                 account_service: AccountService,
                 profile_service: ProfileService,
                 role_service: RoleService,
                 ) -> None:
        super().__init__(repository)
        self.account_service = account_service
        self.profile_service = profile_service
        self.role_service = role_service

    @override
    async def add(self, model: UserModel) -> UserModel:
        if not model.account or not model.profile:
            raise ValueError("UserModel must have account and profile data for creation.")

        persisted_account = await self.account_service.add(model.account)
        persisted_profile = await self.profile_service.add(model.profile)

        default_role = await self.role_service.find_by_name("Base User")
        if not default_role:
            raise EntityNotFound("Default role 'Base User' not found in the database.")

        if persisted_account.id is None or persisted_profile.id is None or default_role.id is None:
            raise ValueError("Component ID is None after creation.")

        user_to_persist = UserModel(
            account_id=persisted_account.id,
            profile_id=persisted_profile.id,
            role_id=default_role.id,
        )
        
        persisted_user = await super().add(user_to_persist)
        
        persisted_user.account = persisted_account
        persisted_user.profile = persisted_profile
        persisted_user.role = default_role

        return persisted_user

    @override
    async def find_by_id(self, id: Positive[int]) -> Optional[UserModel]:
        user = await super().find_by_id(id)
        if not user:
            return None

        account = await self.account_service.find_by_id(user.account_id)
        profile = await self.profile_service.find_by_id(user.profile_id)
        role = await self.role_service.find_by_id(user.role_id)

        if not account or not profile or not role:
            raise ValueError(f"Data inconsistency for User ID {id}: missing account, profile, or role.")

        user.account = account
        user.profile = profile
        user.role = role

        return user
