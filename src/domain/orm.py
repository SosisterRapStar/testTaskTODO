from sqlalchemy import URL
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncAttrs,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import Mapped, DeclarativeBase
from src.config import settings
from sqlalchemy import URL
import datetime
from typing import Annotated
import uuid
from sqlalchemy import text
from sqlalchemy.orm import mapped_column


created_at_timestamp = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
updated_at_timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now
    ),
]

UUIDpk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUIDpk]

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}"

    def __str__(self):
        return self.__repr__()


def create_url_for_db():
    return URL.create(
        "postgresql+asyncpg",
        username=settings.db.db_user,
        password=settings.db.db_password,
        host=settings.db.db_host,
        database=settings.db.db_name,
        port=settings.db.db_port,
    )


class DatabaseHandler:
    session_factory: AsyncSession = async_sessionmaker(
        bind=create_async_engine(url=create_url_for_db(), echo=True),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    @classmethod
    def get_scoped_session(cls) -> AsyncSession:
        session = async_scoped_session(
            session_factory=cls.session_factory,
            scopefunc=current_task,
        )
        return session
