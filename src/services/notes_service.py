from dataclasses import dataclass
from adapters.repository import AbstractNotesRepo, AbstractUserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.schemas import NoteSchema
from src.domain.entities import Note, Tag
from typing import List
from fastapi import HTTPException
from src.domain.entities import User


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
        return new_note

    async def get_users_note(self, current_user: User, id: str) -> Note:
        await current_user.awaitable_attrs.notes
        for note in current_user.notes:
            if str(note.id) == id:
                return note

    async def get_notes_by_tag(self, user_id: str, tags: List[str]) -> List[Note]:
        return await self.repository.get_by_tags(user_id=user_id, tags=tags)

    async def update_note(self, id: str, note: NoteSchema, user: User) -> Note:
        await user.awaitable_attrs.notes
        for note in user.notes:
            if note.id == id:
                updates = note.model_dump(exclude_defaults=True)
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
