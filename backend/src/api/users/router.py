from typing import Annotated

from fastapi import APIRouter, Depends

from src.services.users import UsersService, JWTService
from src.schemas.users import UserDTO, UserPermissions, UserCreateSchema, UserUpdateSchema

from src.utils import exceptions, responses
from src.utils.unitofwork import UnitOfWork

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post(
    path='/',
    responses={
        **responses.ObjectCreated.docs,
        **exceptions.NotAcceptableHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def create_user(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        user_create: UserCreateSchema,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    user_id = await UsersService.create(uow, current_user, user_create)
    return responses.ObjectCreated.response(id=user_id)


@router.get(
    path='/',
    response_model=UserDTO,
    responses={
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def get_user(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        user_id: int | None = None,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    return await UsersService.get(uow, current_user, user_id)


@router.patch(
    path='/',
    responses={
        **responses.ObjectUpdated.docs,
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def update_user(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        user_update: UserUpdateSchema,
        user_id: int | None = None,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    await UsersService.edit(uow, current_user, user_id, user_update)
    return responses.ObjectUpdated.response()


@router.put(
    path='/permissions',
    responses={
        **responses.ObjectUpdated.docs,
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def update_user_permissions(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        user_id: int,
        permissions: UserPermissions,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    await UsersService.change_permissions(uow, current_user, user_id, permissions)
    return responses.ObjectUpdated.response()


@router.post(
    path='/ban',
    responses={
        **responses.ObjectUpdated.docs,
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def ban_user(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        user_id: int,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    await UsersService.ban(uow, current_user, user_id)
    return responses.ObjectUpdated.response()
