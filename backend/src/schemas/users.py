import datetime

from pydantic import BaseModel, EmailStr


class UserPermissions(BaseModel):
    can_view_users: bool
    can_add_users: bool
    can_ban_users: bool
    can_delete_users: bool
    can_edit_user_profile: bool
    can_edit_user_permissions: bool
    super_user: bool


class UserDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    username: str
    password: str | None
    banned: bool
    permissions: UserPermissions
    excluded_categories: list[str]
    created_at: datetime.datetime

    api_keys: list['UserAPIKeyDTO'] | None = None


class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    permissions: UserPermissions


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    excluded_categories: list[str] | None = None


class UserAPIKeyDTO(BaseModel):
    id: int
    key: str
    user_id: int
    expire_date: datetime.date
    created_at: datetime.datetime

    user: UserDTO | None = None

