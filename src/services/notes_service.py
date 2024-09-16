from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.schemas import NoteSchema
from src.domain.entities import Note, Tag


@dataclass
class NotesService:
    repository: AbstractNotesRepo
    session: AsyncSession

    async def create_new_note(self, note: NoteSchema):
        new_note = self.repository.create(
            title=note.title, tags=[tag.name for tag in note.tags]
        )
        await self.session.commit()

    async def add_new_tag(self, note_id: str, tag_name: str):
        note = self.repository.get(id=note_id)
        new_tag = Tag(name=tag_name)
        await note.awaitable_attrs.tags
        self.session.add(new_tag)
        note.tags.append(new_tag)
