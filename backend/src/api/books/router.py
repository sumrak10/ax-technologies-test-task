from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from src.schemas.books import BookDTO, BookAPISchema
from src.schemas.users import UserDTO
from src.services.books import BooksService, LibraryService
from src.services.users import APIKeyService

from src.utils import exceptions, responses
from src.utils.unitofwork import UnitOfWork

router = APIRouter(
    prefix='/books',
    tags=['books']
)


@router.get(
    path='/search',
    response_model=list[BookAPISchema],
    responses={
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
@cache(expire=3)
async def search(
        gb_id: str | None = None,
        query: str | None = None,
        intitle: str | None = None,
        inauthor: str | None = None,
        isbn: str | None = None,
        categories: list[str] | None = None,
):
    return await BooksService.search(
        gb_id,
        query,
        intitle,
        inauthor,
        isbn,
        categories
    )


@router.get(
    path='/isbn',
    response_model=BookDTO,
    responses={
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.NotAcceptableHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
@cache(expire=3)
async def get_by_ISBN(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        isbn: str,
        current_user: UserDTO = Depends(APIKeyService.get_current_user)
):
    return await BooksService.get_by_ISBN(uow, current_user, isbn)


@router.get(
    path='/',
    response_model=list[BookDTO],
    responses={
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
@cache(expire=3)
async def get_user_library(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        current_user: UserDTO = Depends(APIKeyService.get_current_user)
):
    return await LibraryService.get_user_library(uow, current_user)


@router.post(
    path='/',
    responses={
        **responses.ObjectCreated.docs,
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def add_book_in_user_library(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        id: int | None = None,
        gb_id: str | None = None,
        current_user: UserDTO = Depends(APIKeyService.get_current_user)
):
    lib_id = await LibraryService.add_one_in_user_library(uow, current_user, id, gb_id)
    return responses.ObjectCreated.response(id=lib_id)


@router.delete(
    path='/',
    responses={
        **responses.ObjectDeleted.docs,
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def remove_one_from_user_library(
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        id: int | None = None,
        gb_id: str | None = None,
        current_user: UserDTO = Depends(APIKeyService.get_current_user)
):
    await LibraryService.remove_one_from_user_library(uow, current_user, id, gb_id)
    return responses.ObjectDeleted.response()
