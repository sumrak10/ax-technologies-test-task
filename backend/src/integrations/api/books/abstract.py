from abc import ABC, abstractmethod

from ..client import AbstractSessionClient


class AbstractBooksAPI(ABC):
    session_client: AbstractSessionClient = None

    @classmethod
    @abstractmethod
    async def get_by_id(cls, id: str):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def search(cls, **filters):
        raise NotImplementedError()
