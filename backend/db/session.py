from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def get_engine():
    """Lazily create engine at request time, not import time."""
    import os

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/policybot",
    )
    return create_async_engine(database_url, echo=False, pool_pre_ping=True)


def get_async_session_local():
    """Lazily create session maker."""
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


# Module-level exports for backwards compatibility
_engine = None
_AsyncSessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def _get_async_session_local():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = get_async_session_local()
    return _AsyncSessionLocal


# Module-level exports
def __getattr__(name):
    if name == "engine":
        return _get_engine()
    if name == "AsyncSessionLocal":
        return _get_async_session_local()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _get_async_session_local()() as session:
        yield session
