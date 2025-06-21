from app.user.models import AccountModel, ProfileModel, RoleModel
from app.user.repositories import (
    AccountRepository, AccountFindQuery,
    InMemoryAccountRepository,

    ProfileRepository, ProfileFindQuery,
    InMemoryProfileRepository,

    RoleRepository, RoleFindQuery,
    InMemoryRoleRepository,
)
from app.exceptions import *
from app.utils import HttpxClient
from datetime import date
import pytest

@pytest.mark.parametrize('account_repo,profile_repo,role_repo', [
    (InMemoryAccountRepository(), InMemoryProfileRepository(), InMemoryRoleRepository())
])
async def test_register_user(account_repo: AccountRepository,
                             profile_repo: ProfileRepository,
                             role_repo: RoleRepository
                             ) -> None:
    await role_repo.create_defaults()
    assert await role_repo.find_by_name("Base User") is not None, "Base User role should exist."
    assert await role_repo.find_by_name("Family Medicine Doctor") is not None, "Family Medicine Doctor role should exist."
    assert await role_repo.find_by_name("Administrator") is not None, "Administrator role should exist."

    new_profile = ProfileModel(
        name="Elena",
        paternal="Rodriguez",
        maternal="Garcia",
        phone=77712345,
        birthdate=date(1995, 10, 26)
    )
    new_profile = await profile_repo.add(new_profile)
    assert new_profile.id is not None, "Profile should have an ID after being added."

    new_account = AccountModel(
        email="elena.rg@example.com",
        password=b"elena_secure_pwd",
        profile_id=new_profile.id,
        role_id=(await role_repo.find_by_name("Base User")).id
    )
    new_account = await account_repo.add(new_account)
    assert new_account.id is not None, "Account should have an ID after being added."

    stored_account = await account_repo.find_by_id(new_account.id)
    assert stored_account == new_account

    stored_profile = await profile_repo.find_by_id(new_profile.id)
    assert stored_profile == new_profile

    new_profile = ProfileModel(
        name="Uvuvwevwevwe Onyentenyevwe",
        paternal="Ugwemuhwem",
        maternal="Ossas",
        phone=65829984,
        birthdate=date(1987, 6, 6)
    )
    new_profile = await profile_repo.add(new_profile)
    assert new_profile.id is not None, "Profile should have an ID after being added."

    new_account = AccountModel(
        email="admin@example.com",
        password=b"admin_secure_pwd",
        profile_id=new_profile.id,
        role_id=(await role_repo.find_by_name("Administrator")).id
    )
    new_account = await account_repo.add(new_account)
    assert new_account.id is not None, "Account should have an ID after being added."

    cursor = await account_repo.find(AccountFindQuery(order_by=('email', 'asc')))
    assert cursor is not None
    admin = cursor.data[0]
    elena = cursor.data[1]
    assert admin.email == "admin@example.com"
    assert elena.email == "elena.rg@example.com"

    cursor = await account_repo.find(AccountFindQuery(order_by=('id', 'desc')))
    assert cursor is not None
    elena = cursor.data[1]
    admin = cursor.data[0]
    assert elena.email == "elena.rg@example.com"
    assert admin.email == "admin@example.com"


# @pytest.mark.asyncio
# async def test_update_existing_user(account_repo: InMemoryAccountRepository,
#                                     profile_repo: InMemoryProfileRepository
#                                     ) -> None:
#     """
#     **Real Use Case:** Modifying existing user details (e.g., email or account status)
#     and their associated profile information (e.g., phone number).
#     """

#     initial_profile = ProfileModel(
#         name="Carlos", paternal="Lopez", maternal="Perez",
#         birthdate=date(1989, 7, 1), phone=78901234
#     )
#     await profile_repo.add(initial_profile)
#     initial_account = AccountModel(
#         email="carlos.lp@example.com",
#         password=b"carlos_pwd",
#         enabled=True,
#         profile_id=initial_profile.id
#     )
#     await account_repo.add(initial_account)

#     account_to_update = await account_repo.find_by_id(Positive(initial_account.id))
#     account_to_update.email = "carlos.updated@example.com"
#     account_to_update.enabled = False
#     await account_repo.update(Positive(account_to_update.id), account_to_update)

#     profile_to_update = await profile_repo.find_by_id(Positive(initial_profile.id))
#     profile_to_update.phone = 79990000
#     await profile_repo.update(Positive(profile_to_update.id), profile_to_update)

#     verified_account = await account_repo.find_by_id(Positive(initial_account.id))
#     verified_profile = await profile_repo.find_by_id(Positive(initial_profile.id))

#     assert verified_account.email == "carlos.updated@example.com"
#     assert verified_account.enabled is False
#     assert verified_profile.phone == 79990000


# ---
# ## Advanced Data Retrieval (Filtering and Pagination)
# ---

# @pytest.mark.asyncio
# async def test_find_accounts_with_filters_and_simulated_pagination(
#     account_repo: InMemoryAccountRepository,
#     profile_repo: InMemoryProfileRepository
# ):
#     """
#     **Real Use Case:** Fetching lists of accounts using various filter criteria
#     (e.g., email pattern, enabled status) and demonstrating pagination.
#     """

#     users_data = [
#         {"email": "alpha@example.com", "name": "Alpha One", "enabled": True, "birthyear": 1990},
#         {"email": "beta@test.com", "name": "Beta Two", "enabled": False, "birthyear": 1991},
#         {"email": "gamma@example.com", "name": "Gamma Three", "enabled": True, "birthyear": 1992},
#         {"email": "delta@test.com", "name": "Delta Four", "enabled": False, "birthyear": 1993},
#         {"email": "epsilon@example.com", "name": "Epsilon Five", "enabled": True, "birthyear": 1994},
#     ]

#     for i, data in enumerate(users_data):
#         profile = ProfileModel(
#             name=data["name"], paternal="P", maternal="M",
#             birthdate=date(data["birthyear"], 1, 1), phone=70000000 + i
#         )
#         await profile_repo.add(profile)
#         account = AccountModel(
#             email=data["email"], password=b"pass",
#             enabled=data["enabled"], profile_id=profile.id
#         )
#         await account_repo.add(account)

#     enabled_filter = AccountFilterBy(enabled=True)
#     order_by_email_asc: list[OrderBy[AccountAttribute]] = [('email', 'asc')]

#     page_result_enabled = await account_repo.find(
#         filter_by=enabled_filter,
#         order_by=order_by_email_asc
#     )

#     assert len(page_result_enabled.data) == account_repo.page_size_max, "Should respect page_size_max for initial fetch."
#     assert page_result_enabled.data[0].email == "alpha@example.com"
#     assert page_result_enabled.data[1].email == "epsilon@example.com"
#     assert page_result_enabled.next.last is not None, "next.last cursor should be set for next page."

#     regex_filter = AccountFilterBy(email=RegEx("example.com"))

#     page_result_regex_next = await account_repo.find(
#         filter_by=regex_filter,
#         order_by=order_by_email_asc
#     )

#     assert len(page_result_regex_next.data) == account_repo.page_size_max
#     assert page_result_regex_next.data[0].email == "alpha@example.com"
#     assert page_result_regex_next.data[1].email == "epsilon@example.com"


# ---
# ## Deleting User Accounts
# ---

# @pytest.mark.asyncio
# async def test_delete_user_account_impacts_linked_profile(
#     account_repo: InMemoryAccountRepository,
#     profile_repo: InMemoryProfileRepository
# ):
#     """
#     **Real Use Case:** Deleting a user account and verifying its removal.
#     Also, observe the impact on its associated profile (by default, it remains
#     unless `ON DELETE CASCADE` is explicitly configured).
#     """

#     profile_for_deletion = ProfileModel(
#         name="Delete", paternal="Me", maternal="Soon",
#         birthdate=date(1975, 5, 20), phone=75556666
#     )
#     await profile_repo.add(profile_for_deletion)
#     account_for_deletion = AccountModel(
#         email="purge.me@example.com",
#         password=b"temp_pwd",
#         profile_id=profile_for_deletion.id
#     )
#     await account_repo.add(account_for_deletion)

#     initial_account_id = account_for_deletion.id
#     initial_profile_id = profile_for_deletion.id

#     await account_repo.find_by_id(Positive(initial_account_id))
#     await profile_repo.find_by_id(Positive(initial_profile_id))

#     await account_repo.delete(Positive(initial_account_id))

#     with pytest.raises(ValueError, match=f"AccountModel with ID {initial_account_id} not found."):
#         await account_repo.find_by_id(Positive(initial_account_id))

#     remaining_profile = await profile_repo.find_by_id(Positive(initial_profile_id))
#     assert remaining_profile is not None, "Profile should still exist, as DELETE CASCADE isn't set."
#     assert remaining_profile.id == initial_profile_id
