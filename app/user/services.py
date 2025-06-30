from app.user.repositories import (
    AccountRepository, AccountFindQuery,
    ProfileRepository, ProfileFindQuery,
    RoleRepository, RoleFindQuery,
    UserRepository, UserFindQuery,
)
from app.user.models import AccountModel, ProfileModel, RoleModel, UserModel
from app.base.services import BaseService
from app.exceptions import *
from app.utils import Positive
from datetime import datetime, date
from typing import override

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

    async def get_paternal(self, id: Positive[int]) -> str:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.paternal

    async def get_maternal(self, id: Positive[int]) -> str:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.maternal

    async def get_phone(self, id: Positive[int]) -> int | None:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.phone

    async def get_birthdate(self, id: Positive[int]) -> date:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        return profile.birthdate

    async def update_name(self, id: Positive[int], name: str) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.name = name
        return await self.repo.update(id, profile)

    async def update_paternal(self, id: Positive[int], paternal: str) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.paternal = paternal
        return await self.repo.update(id, profile)

    async def update_maternal(self, id: Positive[int], maternal: str) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.maternal = maternal
        return await self.repo.update(id, profile)

    async def update_phone(self, id: Positive[int], phone: int | None) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.phone = phone
        return await self.repo.update(id, profile)

    async def update_birthdate(self, id: Positive[int], birthdate: date) -> ProfileModel:
        profile: ProfileModel | None = await self.find_by_id(id)
        if not profile:
            raise EntityNotFound()
        profile.birthdate = birthdate
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

    async def find_by_name(self, name: str) -> RoleModel | None:
        return await self.repo.find_by_name(name)

    async def get_users(self, id: Positive[int]) -> list[UserModel]:
        role: RoleModel | None = await self.find_by_id(id)
        if not role:
            raise EntityNotFound()
        return role.users


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

        user_to_persist = UserModel(
            role_id=model.role_id,
        )
        persisted_user = await super().add(user_to_persist)

        if persisted_user.id is None:
            raise ValueError("User ID is None after creation.")

        model.account.id = persisted_user.id
        model.profile.id = persisted_user.id

        persisted_account = await self.account_service.add(model.account)
        persisted_profile = await self.profile_service.add(model.profile)

        if persisted_user.role_id is None:
            raise ValueError("User role_id is None.")

        role = await self.role_service.find_by_id(persisted_user.role_id)
        if not role:
            raise EntityNotFound("Role not found.")

        persisted_user.account = persisted_account
        persisted_user.profile = persisted_profile
        persisted_user.role = role

        return persisted_user

    @override
    async def find_by_id(self, id: Positive[int]) -> UserModel | None:
        user = await super().find_by_id(id)
        if not user:
            return None

        assert user.id and user.role_id

        account = await self.account_service.find_by_id(user.id)
        profile = await self.profile_service.find_by_id(user.id)
        role = await self.role_service.find_by_id(user.role_id)

        if not account or not profile or not role:
            raise ValueError(f"Data inconsistency for User ID {id}: missing account, profile, or role.")

        user.account = account
        user.profile = profile
        user.role = role

        return user

    async def get_created_at(self, id: Positive[int]) -> datetime:
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.created_at

    async def get_role(self, id: Positive[int]) -> RoleModel:
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.role

    async def get_account(self, id: Positive[int]) -> AccountModel:
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.account

    async def get_profile(self, id: Positive[int]) -> ProfileModel:
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        return user.profile

    async def update_role_by_id(self, id: Positive[int], role_id: int) -> UserModel:
        """Update the user's role by role_id."""
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        user.role_id = role_id
        updated = await self.repo.update(id, user)
        role = await self.role_service.find_by_id(role_id)
        if not role:
            raise EntityNotFound("Role not found.")
        updated.role = role
        return updated

    async def update_role_by_name(self, id: Positive[int], role_name: str) -> UserModel:
        """Update the user's role by role name (unique)."""
        user: UserModel | None = await self.find_by_id(id)
        if not user:
            raise EntityNotFound()
        role = await self.role_service.find_by_name(role_name)
        if not role:
            raise EntityNotFound("Role not found.")
        user.role_id = role.id
        updated = await self.repo.update(id, user)
        updated.role = role
        return updated
