from src.schemas.users import UserDTO, UserPermissions, UserCreateSchema, UserUpdateSchema
from .auth import PasswordService

from src.utils import exceptions
from src.utils.unitofwork import UnitOfWork


class UsersService:

    @classmethod
    async def create(cls,
                     uow: UnitOfWork,
                     current_user: UserDTO,
                     user_create: UserCreateSchema,
                     ) -> int:
        if not current_user.permissions.can_add_users:
            raise exceptions.ForbiddenHTTPException()
        if user_create.permissions.super_user and not current_user.permissions.super_user:
            raise exceptions.ForbiddenHTTPException()
        async with uow:
            user = await uow.users.get_one_by_username(user_create.username)
            if user is not None:
                raise exceptions.NotAcceptableHTTPException("There is already an account with the same username")
            user_create.password = PasswordService.get_password_hash(user_create.password)
            user_id = await uow.users.add_one(user_create.model_dump())
            if user_create.permissions.super_user:
                new_permissions = current_user.permissions
                new_permissions.super_user = False
                await uow.users.edit_one(current_user.id, {"permissions": new_permissions.model_dump()})
            await uow.commit()
        return user_id

    @classmethod
    async def get(cls,
                  uow: UnitOfWork,
                  current_user: UserDTO,
                  user_id: int | None,
                  ) -> UserDTO:
        if user_id is None:
            user_id = current_user.id
        if not current_user.permissions.can_view_users and current_user.id != user_id:
            raise exceptions.ForbiddenHTTPException()
        async with uow:
            user = await uow.users.get_one(id=user_id)
            if user is None:
                raise exceptions.NotFoundHTTPException()
            await uow.commit()
        return user

    @classmethod
    async def edit(cls,
                   uow: UnitOfWork,
                   current_user: UserDTO,
                   user_id: int | None,
                   user_update: UserUpdateSchema,
                   ) -> None:
        if user_id is None:
            user_id = current_user.id
        if not current_user.permissions.can_edit_user_profile and current_user.id != user_id:
            raise exceptions.ForbiddenHTTPException()
        async with uow:
            user = await uow.users.get_one(id=user_id)
            if user is None:
                raise exceptions.NotFoundHTTPException()
            await uow.users.edit_one(user.id, user_update.model_dump(exclude_none=True))
            await uow.commit()

    @classmethod
    async def change_permissions(cls,
                                 uow: UnitOfWork,
                                 current_user: UserDTO,
                                 user_id: int,
                                 permissions: UserPermissions
                                 ) -> None:
        if not current_user.permissions.can_edit_user_permissions:
            raise exceptions.ForbiddenHTTPException()
        if permissions.super_user and not current_user.permissions.super_user:
            raise exceptions.ForbiddenHTTPException()
        async with uow:
            user = await uow.users.get_one(id=user_id)
            if user is None:
                raise exceptions.NotFoundHTTPException()
            if user.permissions.super_user:
                raise exceptions.ForbiddenHTTPException()
            if user.permissions.can_edit_user_permissions and not current_user.permissions.super_user:
                raise exceptions.ForbiddenHTTPException()
            await uow.users.edit_one(user_id, {"permissions": permissions.model_dump()})
            if permissions.super_user:
                new_permissions = current_user.permissions
                new_permissions.super_user = False
                await uow.users.edit_one(current_user.id, {"permissions": new_permissions.model_dump()})
            await uow.commit()

    @classmethod
    async def ban(cls,
                  uow: UnitOfWork,
                  current_user: UserDTO,
                  user_id: int | None,
                  ) -> None:
        if not current_user.permissions.can_ban_users:
            raise exceptions.ForbiddenHTTPException()
        async with uow:
            await uow.users.edit_one(user_id, {"banned": True})
            await uow.commit()
