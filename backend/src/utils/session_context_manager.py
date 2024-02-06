import uuid
from abc import ABC, abstractmethod

from starlette.requests import Request

from src.database.database import async_session_maker
from src.utils.logger import logger


class AbstractSessionContextManager(ABC):
    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SessionContextManager:

    def __init__(self, request: Request = None) -> None:
        self._session = None

        self.session_factory = async_session_maker

        if request is not None:
            self.session_id = request.state.session_id
        else:
            logger.debug("Request was not set. May not called in http endpoint")
            self.session_id = str(uuid.uuid4())

    @property
    def session(self):
        if self._session is None:
            raise RuntimeError("An attempt to access the session was unsuccessful. Maybe you forgot to initialize it "
                               "via 'async with' construction")
        return self._session

    @session.setter
    def session(self, value):
        if self._session is not None:
            raise RuntimeError("An attempt was made to initialize a session in another session. Possibly called "
                               "'async with' construct in another 'async with' construct")
        self._session = value
        logger.debug(f"{self.session_id} - Session created and set")

    async def __aenter__(self):
        self.session = self.session_factory()

    async def __aexit__(self, *args):
        await self.rollback()
        await self._session.close()
        self._session = None
        logger.debug(f"{self.session_id} - Session closed")

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
