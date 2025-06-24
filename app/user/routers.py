from fastapi import APIRouter, HTTPException, status, Path, Body
from app.user.repositories import AccountFindQuery, ProfileFindQuery, RoleFindQuery
from app.user.services import AccountService, ProfileService, RoleService, UserService
from app.user.schemas import (
    AccountRequestSchema, AccountResponseSchema,
    ProfileRequestSchema, ProfileResponseSchema,
    RoleRequestSchema, RoleResponseSchema,
    UserResponseSchema, UserRequestSchema
)
from app.user.models import AccountModel, ProfileModel, RoleModel, UserModel
from app.exceptions import *
from app.base.models import Page
from app.utils import Positive, parse_last_retrieved
from collections.abc import Callable
from typing import Annotated
from datetime import datetime

class AccountRouter(APIRouter):
    def __init__(self, prefix: str, account_service_factory: Callable[[], AccountService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = account_service_factory

        self.add_api_route('/', self.post_account, name="Post Account", methods=['post'])
        self.add_api_route('/find', self.find_accounts, name="Find Accounts", methods=['post'])
        self.add_api_route('/{id}', self.get_account, name="Get Account", methods=['get'])
        self.add_api_route('/{id}', self.put_account, name="Put Account", methods=['put'])
        self.add_api_route('/{id}', self.delete_account, name="Delete Account", methods=['delete'])
        self.add_api_route('/{id}/updated_at', self.get_account_updated_at, name="Get Account Updated At", methods=['get'])
        self.add_api_route('/{id}/email', self.get_account_email, name="Get Account Email", methods=['get'])
        self.add_api_route('/{id}/enabled', self.get_account_enabled, name="Get Account Enabled", methods=['get'])
        self.add_api_route('/{id}/email', self.put_account_email, name="Put Account Email", methods=['put'])
        self.add_api_route('/{id}/enabled', self.put_account_enabled, name="Put Account Enabled", methods=['put'])

    async def post_account(self, account: Annotated[AccountRequestSchema, Body()]) -> AccountResponseSchema:
        return AccountResponseSchema.model_validate((await self.svc().add(AccountModel.model_validate(account))).model_dump())

    async def get_account(self, id: Annotated[Positive[int], Path()]) -> AccountResponseSchema:
        try:
            account: AccountModel | None = await self.svc().find_by_id(id)
            if account:
                return AccountResponseSchema.model_validate(account)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_accounts(self, query: Annotated[AccountFindQuery, Body()]) -> Page[AccountResponseSchema, AccountFindQuery] | None:
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), AccountModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page = Page[AccountResponseSchema, AccountFindQuery](
                next=page.next,
                data=[AccountResponseSchema.model_validate(account) for account in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_account(self, id: Annotated[Positive[int], Path()], account: Annotated[AccountRequestSchema, Body()]) -> AccountResponseSchema:
        try:
            model = await self.svc().update(id, AccountModel.model_validate(account))
            return AccountResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def delete_account(self, id: Annotated[Positive[int], Path()]) -> AccountResponseSchema:
        try:
            model = await self.svc().delete(id)
            return AccountResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def get_account_updated_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_updated_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def get_account_email(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_email(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def get_account_enabled(self, id: Annotated[Positive[int], Path()]) -> bool:
        try:
            return await self.svc().get_enabled(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def put_account_email(self, id: Annotated[Positive[int], Path()], email: Annotated[str, Body()]) -> AccountResponseSchema:
        try:
            return AccountResponseSchema.model_validate(await self.svc().update_email(id, email))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

    async def put_account_enabled(self, id: Annotated[Positive[int], Path()], enabled: Annotated[bool, Body()]) -> AccountResponseSchema:
        try:
            return AccountResponseSchema.model_validate(await self.svc().update_enabled(id, enabled))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")

class ProfileRouter(APIRouter):
    def __init__(self, prefix: str, profile_service_factory: Callable[[], ProfileService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = profile_service_factory

        self.add_api_route('/', self.post_profile, name="Post Profile", methods=['post'])
        self.add_api_route('/find', self.find_profiles, name="Find Profiles", methods=['post'])
        self.add_api_route('/{id}', self.get_profile, name="Get Profile", methods=['get'])
        self.add_api_route('/{id}', self.put_profile, name="Put Profile", methods=['put'])
        self.add_api_route('/{id}', self.delete_profile, name="Delete Profile", methods=['delete'])
        self.add_api_route('/{id}/updated_at', self.get_profile_updated_at, name="Get Profile Updated At", methods=['get'])
        self.add_api_route('/{id}/name', self.get_profile_name, name="Get Profile Name", methods=['get'])
        self.add_api_route('/{id}/name', self.put_profile_name, name="Put Profile Name", methods=['put'])

    async def post_profile(self, profile: Annotated[ProfileRequestSchema, Body()]) -> ProfileResponseSchema:
        return ProfileResponseSchema.model_validate((await self.svc().add(ProfileModel.model_validate(profile))).model_dump())

    async def get_profile(self, id: Annotated[Positive[int], Path()]) -> ProfileResponseSchema:
        try:
            profile: ProfileModel | None = await self.svc().find_by_id(id)
            if profile:
                return ProfileResponseSchema.model_validate(profile)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_profiles(self, query: Annotated[ProfileFindQuery, Body()]) -> Page[ProfileResponseSchema, ProfileFindQuery] | None:
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), ProfileModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page = Page[ProfileResponseSchema, ProfileFindQuery](
                next=page.next,
                data=[ProfileResponseSchema.model_validate(profile) for profile in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_profile(self, id: Annotated[Positive[int], Path()], profile: Annotated[ProfileRequestSchema, Body()]) -> ProfileResponseSchema:
        try:
            model = await self.svc().update(id, ProfileModel.model_validate(profile))
            return ProfileResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")

    async def delete_profile(self, id: Annotated[Positive[int], Path()]) -> ProfileResponseSchema:
        try:
            model = await self.svc().delete(id)
            return ProfileResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")

    async def get_profile_updated_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_updated_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")

    async def get_profile_name(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_name(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")

    async def put_profile_name(self, id: Annotated[Positive[int], Path()], name: Annotated[str, Body()]) -> ProfileResponseSchema:
        try:
            return ProfileResponseSchema.model_validate(await self.svc().update_name(id, name))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found.")

class RoleRouter(APIRouter):
    def __init__(self, prefix: str, role_service_factory: Callable[[], RoleService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = role_service_factory

        self.add_api_route('/', self.post_role, name="Post Role", methods=['post'])
        self.add_api_route('/find', self.find_roles, name="Find Roles", methods=['post'])
        self.add_api_route('/{id}', self.get_role, name="Get Role", methods=['get'])
        self.add_api_route('/{id}', self.put_role, name="Put Role", methods=['put'])
        self.add_api_route('/{id}', self.delete_role, name="Delete Role", methods=['delete'])
        self.add_api_route('/{id}/created_at', self.get_role_created_at, name="Get Role Created At", methods=['get'])
        self.add_api_route('/{id}/updated_at', self.get_role_updated_at, name="Get Role Updated At", methods=['get'])
        self.add_api_route('/{id}/name', self.get_role_name, name="Get Role Name", methods=['get'])
        self.add_api_route('/{id}/name', self.put_role_name, name="Put Role Name", methods=['put'])

    async def post_role(self, role: Annotated[RoleRequestSchema, Body()]) -> RoleResponseSchema:
        return RoleResponseSchema.model_validate((await self.svc().add(RoleModel.model_validate(role))).model_dump())

    async def get_role(self, id: Annotated[Positive[int], Path()]) -> RoleResponseSchema:
        try:
            role: RoleModel | None = await self.svc().find_by_id(id)
            if role:
                return RoleResponseSchema.model_validate(role)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def find_roles(self, query: Annotated[RoleFindQuery, Body()]) -> Page[RoleResponseSchema, RoleFindQuery] | None:
        try:
            if query.last:
                query.last = parse_last_retrieved(list(query.last), RoleModel, query.order_by)
            page = await self.svc().find(query)
            if not page:
                return None
            response_page = Page[RoleResponseSchema, RoleFindQuery](
                next=page.next,
                data=[RoleResponseSchema.model_validate(role) for role in page.data],
            )
            return response_page
        except ConnectionTimeout:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database connection timeout.")

    async def put_role(self, id: Annotated[Positive[int], Path()], role: Annotated[RoleRequestSchema, Body()]) -> RoleResponseSchema:
        try:
            model = await self.svc().update(id, RoleModel.model_validate(role))
            return RoleResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

    async def delete_role(self, id: Annotated[Positive[int], Path()]) -> RoleResponseSchema:
        try:
            model = await self.svc().delete(id)
            return RoleResponseSchema.model_validate(model)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

    async def get_role_created_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_created_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

    async def get_role_updated_at(self, id: Annotated[Positive[int], Path()]) -> datetime:
        try:
            return await self.svc().get_updated_at(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

    async def get_role_name(self, id: Annotated[Positive[int], Path()]) -> str:
        try:
            return await self.svc().get_name(id)
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

    async def put_role_name(self, id: Annotated[Positive[int], Path()], name: Annotated[str, Body()]) -> RoleResponseSchema:
        try:
            return RoleResponseSchema.model_validate(await self.svc().update_name(id, name))
        except EntityNotFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")

class UserRouter(APIRouter):
    def __init__(self, prefix: str, user_service_factory: Callable[[], UserService]) -> None:
        super().__init__(prefix=prefix)
        self.svc = user_service_factory
        self.add_api_route('/', self.post_user, name="Post User", methods=['post'])
        self.add_api_route('/{user_id}', self.get_user, name="Get User", methods=['get'])

    async def post_user(self, user: Annotated[UserRequestSchema, Body()]) -> UserResponseSchema:
        account = AccountModel.model_validate(user.account)
        profile = ProfileModel.model_validate(user.profile)
        user_model = UserModel(
            account=account,
            profile=profile
        )
        model = await self.svc().add(user_model)
        return UserResponseSchema.model_validate(model)

    async def get_user(self, user_id: Annotated[Positive[int], Path()]) -> UserResponseSchema:
        user = await self.svc().find_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        return UserResponseSchema.model_validate(user)
