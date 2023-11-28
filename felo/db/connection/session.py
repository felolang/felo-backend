# mypy: ignore-errors
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from felo.config.utils import CONFIG


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
            future=True,
        )

    def refresh(self) -> None:
        self.engine = create_async_engine(
            CONFIG.database_uri,
            echo=True,
            future=True,
            pool_size=20,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
        )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session


__all__ = [
    "get_session",
]
