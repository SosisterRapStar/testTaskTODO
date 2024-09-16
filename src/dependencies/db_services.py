from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.orm import DatabaseHandler
from typing import AsyncGenerator
from src.services.user_service import UserService
from src.services.notes_service import NotesService
from src.adapters.repository import UserRepo, NotesRepo


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = DatabaseHandler.get_scoped_session()
    async with session() as session:
        yield session


session_dep = Annotated[AsyncSession, Depends(get_session)]


async def get_user_service(session: session_dep) -> UserService:
    UserService(user_repo=UserRepo(session=session), session=session)
    return UserService


async def get_notes_service(session: session_dep) -> NotesService:
    NotesService(
        user_repository=UserRepo(session=session),
        repository=NotesRepo(session=session),
        session=session,
    )
    return NotesService


user_service = Annotated[UserService, Depends(get_user_service)]
notes_service = Annotated[NotesService, Depends(get_notes_service)]
