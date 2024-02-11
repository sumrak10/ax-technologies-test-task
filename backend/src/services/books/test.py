import pytest
from unittest.mock import Mock, AsyncMock
from src.services.books import BooksService, LibraryService
from src.schemas.books import BookDTO, BookAPISchema
from src.utils import exceptions
from src.utils.unitofwork import UnitOfWork


@pytest.mark.asyncio
async def test_search_books():
    with pytest.raises(exceptions.NotAcceptableHTTPException):
        await BooksService.search(gb_id=None, query=None, intitle=None, inauthor=None, isbn=None,
                                  categories=None)
    with pytest.raises(exceptions.NotAcceptableHTTPException):
        await BooksService.search(gb_id="aOgOAQAAMAAJ", query='Python', intitle=None, inauthor=None, isbn=None,
                                  categories=None)
    res = await BooksService.search(gb_id="aOgOAQAAMAAJ", query=None, intitle=None, inauthor=None, isbn=None,
                                    categories=None)
    assert isinstance(res, list)
    assert isinstance(res[0], BookAPISchema)
    assert res[0].gb_id == "aOgOAQAAMAAJ"


@pytest.mark.asyncio
async def test_get_book_by_ISBN():
    mock_book_model = Mock(spec=BookDTO)
    mock_book_model.isbn = "1887902996"
    mock_book_model.categories = "Programming"

    mock_books = AsyncMock()
    mock_books.get_one.return_value = mock_book_model

    mock_uow = AsyncMock(spec=UnitOfWork)
    mock_uow.books = mock_books

    mock_user = Mock()
    mock_user.excluded_categories = []

    res = await BooksService.get_by_ISBN(mock_uow, mock_user, "1887902996")
    assert isinstance(res, BookDTO)
    assert res.isbn == "1887902996"

    mock_user = Mock()
    mock_user.excluded_categories = ["Programming"]

    res = await BooksService.get_by_ISBN(mock_uow, mock_user, "1887902996")
    assert res is None


@pytest.mark.asyncio
async def test_get_user_library():
    mock_book_model = Mock(spec=BookDTO)
    mock_book_model.isbn = "1887902996"
    mock_book_model.categories = "Programming"

    mock_books = AsyncMock()
    mock_books.get_user_library.return_value = [mock_book_model]

    mock_uow = AsyncMock(spec=UnitOfWork)
    mock_uow.books = mock_books

    mock_user = Mock()

    res = await LibraryService.get_user_library(mock_uow, mock_user)
    assert len(res) == 1
    assert isinstance(res[0], BookDTO)


@pytest.mark.asyncio
async def test_add_book_in_local_db():
    mock_books = AsyncMock()
    mock_books.add_one.return_value = 1

    mock_uow = AsyncMock(spec=UnitOfWork)
    mock_uow.books = mock_books

    mock_gb_book = Mock(spec=BookAPISchema)
    mock_gb_book.model_dump.return_value = {"title": "Python Programming"}

    result = await LibraryService.add_book_in_local_db(mock_uow, mock_gb_book)
    assert result == 1
