# mypy: ignore-errors
import os
from typing import AsyncGenerator

import asyncpg
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes, create_async_connector
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from felo.config.utils import CONFIG


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    google_connector = None

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    @classmethod
    async def create(cls):
        if not cls.google_connector:
            print("creating google_connector")
            cls.google_connector = await create_async_connector(
                IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
            )
        return cls()

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
            future=True,
        )

    async def get_conn_goole(self) -> asyncpg.Connection:
        conn: asyncpg.Connection = await self.google_connector.connect_async(
            CONFIG.SQL_CLOUD_INSTANCE_CONNECTION_NAME,
            "asyncpg",
            user=CONFIG.POSTGRES_USER,
            password=CONFIG.POSTGRES_PASSWORD,
            db=CONFIG.POSTGRES_DB,
        )
        return conn

    def refresh(self) -> None:
        if CONFIG.ENV == "dev":
            self.engine = create_async_engine(
                CONFIG.database_uri,
                echo=True,
                future=True,
                pool_size=20,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1800,
            )
        else:
            self.engine = create_async_engine(
                "postgresql+asyncpg://",
                async_creator=self.get_conn_goole,
                echo=True,
                future=True,
                pool_size=20,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1800,
            )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_manager = await SessionManager().create()
    session_maker = session_manager.get_session_maker()
    async with session_maker() as session:
        yield session


__all__ = [
    "get_session",
]
