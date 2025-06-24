from app.base.models import BaseModel, Field
from datetime import datetime, date
from typing import Annotated, Optional

class AccountRequestSchema(BaseModel):
    email: Annotated[str, Field(max_length=127)]
    password: Annotated[bytes, Field(max_length=32)]
    enabled: Annotated[bool, Field(default=True)]
    # profile_id and role_id are not required for creation
    profile_id: Optional[int] = None
    role_id: Optional[int] = None

class AccountResponseSchema(AccountRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]

class ProfileRequestSchema(BaseModel):
    name: Annotated[str, Field(max_length=63)]
    paternal: Annotated[str, Field(max_length=31)]
    maternal: Annotated[str, Field(max_length=31)]
    phone: Annotated[Optional[int], Field(ge=60_000_000, lt=80_000_000, default=None)]
    birthdate: Annotated[date, Field()]

class ProfileResponseSchema(ProfileRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]

class RoleRequestSchema(BaseModel):
    name: Annotated[str, Field(max_length=127)]

class RoleResponseSchema(RoleRequestSchema):
    id: Annotated[int, Field(gt=0)]
    created_at: Annotated[datetime, Field()]

class UserRequestSchema(BaseModel):
    profile: ProfileRequestSchema
    account: AccountRequestSchema
    role: RoleRequestSchema

class UserResponseSchema(BaseModel):
    account: AccountResponseSchema
    profile: ProfileResponseSchema
    role: RoleResponseSchema
