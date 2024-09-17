from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo, AbstractUserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.schemas import NoteSchema, NoteForUpdate
from src.domain.entities import Note, Tag
from typing import List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.domain.entities import User
import uuid

@dataclass
class NotesService:
    repository: AbstractNotesRepo
    user_repository: AbstractUserRepo
    session: AsyncSession

    async def create_new_note(self, user: User, note: NoteSchema) -> Note:
        new_note = await self.repository.create(
            title=note.title, tags=[tag.name for tag in note.tags], user_id=str(user.id)
        )
        await self.session.commit()
        return new_note.id

    async def get_users_note(self, current_user: User, id: uuid.UUID) -> Note:
        for note in current_user.notes:
            if note.id == id:
                return note
            
    async def get_users_notes(self, user: User) -> List[Note]:
        await user.awaitable_attrs.notes
        return user.notes


    async def get_notes_by_tag(self, user: User, tags: List[str]) -> List[Note]:
        return await self.repository.get_by_tags(user_id=user.id, tags=tags)

    async def update_note(self, id: str, note_schema: NoteForUpdate, user: User) -> Note:
      
        for note in user.notes:
            if note.id == id:
                updates = note_schema.model_dump(exclude_none=True)
                note = await self.repository.update(id=id, updates=updates)
                await self.session.commit()
                return note
        raise HTTPException(status_code=403, detail="Has no permissions")

    async def delete_note(self, id: str, user: User) -> Note:
        await user.awaitable_attrs.notes
        for note in user.notes:
            if note.id == id:
                await self.repository.delete(id=id)
                await self.session.commit()

        raise HTTPException(status_code=403, detail="Has no permissions")