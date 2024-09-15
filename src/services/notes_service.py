from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class NotesService:
    repository: AbstractNotesRepo
    session: AsyncSession

    # async def create_new_note(self, note:):
