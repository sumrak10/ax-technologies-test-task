import hashlib
from typing import Callable, Optional

from starlette.requests import Request
from starlette.responses import Response

from src.utils.logger import logger


def default_key_builder(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    from fastapi_cache import FastAPICache
    try:
        kwargs.pop('uow')
    except KeyError:
        pass
    try:
        kwargs.pop('session')
    except KeyError:
        pass
    cache_key = (
        f"{FastAPICache.get_prefix()}:{namespace}:"
        + hashlib.md5(
            f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode()
        ).hexdigest()
    )
    return cache_key


def exclude_current_user_key_builder(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    from fastapi_cache import FastAPICache
    kwargs.pop('current_user')
    cache_key = (
        f"{FastAPICache.get_prefix()}:{namespace}:"
        + hashlib.md5(
            f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode()
        ).hexdigest()
    )
    return cache_key