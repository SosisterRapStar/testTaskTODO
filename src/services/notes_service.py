from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo, AbstractUserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.schemas import NoteSchema
from src.domain.entities import Note, Tag
from typing import List
from fastapi import HTTPException


@dataclass
class NotesService:
    repository: AbstractNotesRepo
    user_repository: AbstractUserRepo
    session: AsyncSession

    async def create_new_note(self, note: NoteSchema) -> Note:
        new_note = self.repository.create(title=note.title, tags=[tag.name for tag in note.tags])
        await self.session.commit()
        return new_note
    
    async def get_notes_by_tag(self, user_id: str, tags: List[str]) -> List[Note]:
        return await self.repository.get_by_tags(user_id=user_id, tags=tags)

    async def update_note(self, id: str, note: NoteSchema) -> Note:
        updates = note.model_dump(exclude_defaults=True)
        note = await self.repository.update(id=id, updates=updates)
        await self.session.commit()
        return note
    
    async def delete_note(self, id: str) -> Note:
        if await self.user_repository.has_note:
            await self.repository.delete(id=id)
            await self.session.commit()
        else:
            raise HTTPException(status_code=403, detail="Has no permissions")

        
