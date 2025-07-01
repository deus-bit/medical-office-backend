from app.user.repositories import (
    AccountRepository, AccountFindQuery,
    InMemoryAccountRepository,

    ProfileRepository, ProfileFindQuery,
    InMemoryProfileRepository,

    RoleRepository, RoleFindQuery,
    InMemoryRoleRepository,

    UserRepository, UserFindQuery,
    InMemoryUserRepository,
)
from app.user.services import UserService, AccountService, ProfileService, RoleService
from app.user.schemas import UserRequestSchema, UserResponseSchema, AccountRequestSchema, AccountResponseSchema, ProfileRequestSchema, ProfileResponseSchema, RoleRequestSchema, RoleResponseSchema
from app.user.models import AccountModel, ProfileModel, RoleModel, UserModel
from app.base.common import SupportsModelPersistance
from app.base.models import Page
from app.exceptions import *
from tests.integration.user import UserApiClient
from random import randint
import pytest
from datetime import date

@pytest.mark.parametrize(
    'account_request_schema,account_response_schema,profile_request_schema,profile_response_schema,' +
    'role_request_schema,role_response_schema,user_request_schema,user_response_schema,' +
    'user_mpo', [
        (AccountModel, AccountModel, ProfileModel, ProfileModel,
            RoleModel, RoleModel, UserModel, UserModel,
            UserService(
                InMemoryUserRepository(),
                lambda: AccountService(InMemoryAccountRepository()),
                lambda: ProfileService(InMemoryProfileRepository()),
                lambda: RoleService(InMemoryRoleRepository())
            )),
        # (AccountRequestSchema, AccountResponseSchema, ProfileRequestSchema, ProfileResponseSchema,
        #     RoleRequestSchema, RoleResponseSchema, UserRequestSchema, UserResponseSchema,
        #     UserApiClient('http://127.0.0.1:8080')
        # ),
    ]
)
async def test_basic_persistance(account_request_schema: type[AccountRequestSchema | AccountModel],
                                 account_response_schema: type[AccountResponseSchema | AccountModel],
                                 profile_request_schema: type[ProfileRequestSchema | ProfileModel],
                                 profile_response_schema: type[ProfileResponseSchema | ProfileModel],
                                 role_request_schema: type[RoleRequestSchema | RoleModel],
                                 role_response_schema: type[RoleResponseSchema | RoleModel],
                                 user_request_schema: type[UserRequestSchema | UserModel],
                                 user_response_schema: type[UserResponseSchema | UserModel],
                                 user_mpo: SupportsModelPersistance[UserRequestSchema | UserModel, UserFindQuery],
                                 ) -> None:
    assert account_request_schema in {AccountModel, AccountRequestSchema}
    assert account_response_schema in {AccountModel, AccountResponseSchema}
    assert profile_request_schema in {ProfileModel, ProfileRequestSchema}
    assert profile_response_schema in {ProfileModel, ProfileResponseSchema}
    assert role_request_schema in {RoleModel, RoleRequestSchema}
    assert role_response_schema in {RoleModel, RoleResponseSchema}
    assert user_request_schema in {UserModel, UserRequestSchema}
    assert user_response_schema in {UserModel, UserResponseSchema}

    user: UserResponseSchema

    role_name = "TestRole"
    await user_mpo.role_service().add(role_request_schema(name=role_name))
    assert user_mpo.role_service().find_by_name(role_name)

    def make_user(i: int) -> UserRequestSchema:
        account: AccountRequestSchema = account_request_schema(
            email=f"user{i}@example.com",
            password=b"password",
            enabled=True
        )
        profile: ProfileRequestSchema = profile_request_schema(
            name=f"User{i}",
            paternal="Test",
            maternal="Case",
            phone=60000000 + i,
            birthdate=date(1990, 1, 1)
        )
        role: RoleRequestSchema = role_request_schema(name=role_name)
        return user_request_schema(account=account, profile=profile, role=role)

    requests: list[UserRequestSchema] = [make_user(i) for i in range(1, 6)]
    responses: list[UserResponseSchema] = []

    for user_request in requests:
        persisted_user = await user_mpo.add(user_request)
        assert persisted_user is not None
        assert persisted_user.id is not None
        responses.append(persisted_user)

    for user in responses:
        assert user.id is not None
        persisted_user = await user_mpo.find_by_id(user.id)
        assert persisted_user is not None
        assert persisted_user == user

    count = 0
    page: Page[UserResponseSchema, UserFindQuery] | None = await user_mpo.find(UserFindQuery(order_by=('created_at', 'desc')))
    assert page is not None
    while page:
        count += len(page.data)
        for i in range(1, len(page.data)):
            assert page.data[i - 1].id and page.data[i].id
            assert page.data[i - 1].created_at > page.data[i].created_at or (
                page.data[i - 1].created_at == page.data[i].created_at and
                page.data[i - 1].id > page.data[i].id
            )
        page = await user_mpo.find(page.next)
    assert count == len(responses)

    user = responses[randint(0, len(responses) - 1)]
    assert user.id is not None
    user.profile.name = "Updated Name"
    persisted_user: user_response_schema = await user_mpo.update(user.id, user)
    assert persisted_user == user

    await user_mpo.delete(user.id)
    assert await user_mpo.find_by_id(user.id) is None
