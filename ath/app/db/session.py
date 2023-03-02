from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core import config

settings = config.get_settings()


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=100,
    max_overflow=100,
)


async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def close_engine():
    await engine.dispose()


async def get_db():
    """
    Creates the actual session/transaction. We're doing two things in a single
    context manager:
        - create a session
        - create a transaction

    It is equivalent to:
    ```
        async with async_session() as session:
            async with session.begin():
                yield session
    ```

    Nested transaction may be created with:
    ```
        with session.begin_nested() as nested:  # BEGIN SAVEPOINT
            nested.add(some_object)
            nested.rollback()  # ROLLBACK TO SAVEPOINT
    ```
    """
    async with async_session_factory() as session:
        # ... setup
        yield session
        # ... teardown
