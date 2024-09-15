from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.orm import DatabaseHandler
from typing import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = DatabaseHandler.get_scoped_session()
    async with session() as session:
        yield session


session_dep = Annotated[AsyncSession, Depends(get_session)]
