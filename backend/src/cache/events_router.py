from fastapi import APIRouter

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from config.redis import redis_settings
from .key_builders import default_key_builder


router = APIRouter()


@router.on_event("startup")
async def startup():
    redis = aioredis.from_url(redis_settings.DSN)
    FastAPICache.init(
        backend=RedisBackend(redis),
        prefix="fastapi-cache",
        expire=3,
        key_builder=default_key_builder
    )
