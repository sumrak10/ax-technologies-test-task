from src.schemas.books import BookAPISchema, BookDTO
from src.schemas.users import UserDTO

from src.integrations.api.books.google_books import GoogleBooksAPI
from src.schemas.books import BookDTO
from src.utils import exceptions
from src.utils.unitofwork import UnitOfWork


class BooksService:

    @classmethod
    async def search(cls,
                     gb_id: str | None = None,
                     query: str | None = None,
                     intitle: str | None = None,
                     inauthor: str | None = None,
                     isbn: str | None = None,
                     categories: list[str] | None = None,
                     ) -> list[BookAPISchema]:
        if not any([gb_id, query, intitle, inauthor, isbn, categories]):
            raise exceptions.NotAcceptableHTTPException("At least one search parameter is required")
        if gb_id is None and (not any([query, intitle, inauthor, isbn, categories])):
            raise exceptions.NotAcceptableHTTPException("If gb_id is empty then at least one of the other parameters "
                                                        "must have a value")
        if gb_id is not None and (any([query, intitle, inauthor, isbn, categories])):
            raise exceptions.NotAcceptableHTTPException("If gb_id is passed, the remaining fields must be empty")
        return await GoogleBooksAPI.search(gb_id, query, intitle, inauthor, isbn, categories)

    @classmethod
    async def get_by_ISBN(cls,
                          uow: UnitOfWork,
                          current_user: UserDTO,
                          isbn: str,
                          ) -> BookDTO | None:
        async with uow:
            book = await uow.books.get_one(ISBN=isbn)
            for category in book.categories.split(', '):
                if category in current_user.excluded_categories:
                    return None
            await uow.commit()
        return book


class LibraryService:
    @classmethod
    async def get_user_library(cls,
                               uow: UnitOfWork,
                               current_user: UserDTO,
                               ) -> list[BookDTO]:
        async with uow:
            books = await uow.books.get_user_library(current_user.id)
            await uow.commit()
        return books

    @classmethod
    async def add_one_in_user_library(cls,
                                      uow: UnitOfWork,
                                      current_user: UserDTO,
                                      id: int | None = None,
                                      gb_id: str | None = None,
                                      ) -> int:
        if id is None and gb_id is None:
            raise exceptions.NotAcceptableHTTPException("At least one of the parameters id or gb_id is required")
        async with uow:
            if id is not None:
                book = await uow.books.get_one(id=id)
                if book is None:
                    raise exceptions.NotFoundHTTPException(f"Book with id={id} not found. Try add by gb_id/")
                book_id = book.id
            else:
                book = await uow.books.get_one(gb_id=gb_id)
                if book is None:
                    gb_book = await GoogleBooksAPI.get_by_id(gb_id)
                    book_id = await cls.add_book_in_local_db(uow, gb_book)
                else:
                    book_id = book.id
            association = await uow.books.users_library_repo.get_association(book_id, current_user.id)
            if association is not None:
                raise exceptions.NotAcceptableHTTPException("This book is already in the user's library")
            book_association = await uow.books.users_library_repo.add_association(book_id, current_user.id)
            await uow.commit()
        return book_association

    @classmethod
    async def remove_one_from_user_library(cls,
                                           uow: UnitOfWork,
                                           current_user: UserDTO,
                                           id: int | None = None,
                                           gb_id: str | None = None,
                                           ) -> None:
        if id is None and gb_id is None:
            raise exceptions.NotAcceptableHTTPException("At least one of the parameters id or gb_id is required")
        async with uow:
            if id is not None:
                book = await uow.books.get_one(id=id)
                if book is None:
                    raise exceptions.NotFoundHTTPException(f"Book with id={id} not found. Try add by gb_id/")
                book_id = book.id
            else:
                book = await uow.books.get_one(gb_id=gb_id)
                if book is None:
                    gb_book = await GoogleBooksAPI.get_by_id(gb_id)
                    book_id = await cls.add_book_in_local_db(uow, gb_book)
                else:
                    book_id = book.id
            book_association = await uow.books.users_library_repo.del_association(book_id, current_user.id)
            await uow.commit()

    # UTILS
    @classmethod
    async def add_book_in_local_db(cls,
                                   uow: UnitOfWork,
                                   gb_book: BookAPISchema
                                   ) -> int:
        return await uow.books.add_one(gb_book.model_dump())
