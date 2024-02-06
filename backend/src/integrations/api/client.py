from abc import ABC, abstractmethod
from typing import Any

import aiohttp

from src.schemas.books import BookDTO


class AbstractSessionClient:
    @abstractmethod
    def __init__(self, base_url: str):
        self.BASE_URL = base_url
        raise NotImplementedError()

    @abstractmethod
    async def get(self, url: str, params: dict[str, str], headers: dict[str, str], **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def post(self, url: str, params: dict[str, str], data: dict[str, Any], headers: dict[str, str], **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def put(self, url: str, params: dict[str, str], data: dict[str, Any], headers: dict[str, str], **kwargs):
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, url: str, params: dict[str, str], data: dict[str, Any], headers: dict[str, str], **kwargs):
        raise NotImplementedError()


class AioHTTPSessionClient(AbstractSessionClient):
    def __init__(self, base_url: str):
        self.BASE_URL = base_url

    async def get(self, url: str, params: dict[str, str] = None, headers: dict[str, str] = None, **kwargs
                  ) -> tuple[int, dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL + url, params=params, headers=headers, **kwargs) as resp:
                return resp.status, await resp.json()

    async def post(self, url: str, params: dict[str, str], data: dict[str, Any], headers: dict[str, str], **kwargs
                   ) -> tuple[int, dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL + url, params=params, data=data, headers=headers, **kwargs) as resp:
                return resp.status, await resp.json()

    async def put(self, url: str, params: dict[str, str], data: dict[str, Any], headers: dict[str, str], **kwargs
                  ) -> tuple[int, dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.put(self.BASE_URL + url, params=params, data=data, headers=headers, **kwargs) as resp:
                return resp.status, await resp.json()

    async def delete(self, url: str, params: dict[str, str], headers: dict[str, str], **kwargs
                     ) -> tuple[int, dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.delete(self.BASE_URL + url, params=params, headers=headers, **kwargs) as resp:
                return resp.status, await resp.json()
