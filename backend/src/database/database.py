import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.db import db_settings


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


engine = create_async_engine(
    url=db_settings.DSN,
    pool_size=db_settings.POOL_SIZE,
    max_overflow=db_settings.MAX_POOL_OVERFLOW,
    pool_timeout=db_settings.POOL_TIMEOUT,
    echo=True
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
