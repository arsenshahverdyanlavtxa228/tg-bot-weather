from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.database.models import Base


class SessionFactory:
    def __init__(self, engine: AsyncEngine, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._engine = engine
        self._sessionmaker = sessionmaker

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self) -> None:
        await self._engine.dispose()


def create_engine_and_session(database_url: str) -> SessionFactory:
    engine = create_async_engine(database_url, future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return SessionFactory(engine, sessionmaker)


async def init_models(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
