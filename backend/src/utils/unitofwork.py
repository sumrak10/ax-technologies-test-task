from starlette.requests import Request

from src.database.database import async_session_maker
from src.utils.session_context_manager import SessionContextManager
from src.repositories import *


class UnitOfWork(SessionContextManager):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self.users: UsersRepository = None

        self.books: BooksRepository = None

    async def __aenter__(self):
        if self._session is not None:
            raise RuntimeError("Session init in other session")
        self.session = self.session_factory()
        self.init_repositories()

    def init_repositories(self):
        self.users = UsersRepository(self.session)

        self.books = BooksRepository(self.session)
