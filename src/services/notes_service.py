from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.schemas import NoteSchema

@dataclass
class NotesService:
    repository: AbstractNotesRepo
    session: AsyncSession

    async def create_new_note(self, note: NoteSchema):
        self.repository.create(title=note.title, tags=[tag.name for tag in note.tags])
