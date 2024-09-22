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
from src.config import logger


@dataclass
class NotesService:
    repository: AbstractNotesRepo
    user_repository: AbstractUserRepo
    session: AsyncSession

    async def create_new_note(self, user: User, note: NoteSchema) -> Note:
        try:
            new_note = await self.repository.create(
                title=note.title,
                tags=[tag.name for tag in set(note.tags)],
                user_id=str(user.id),
                content=note.content
            )
            await self.session.commit()
            logger.debug("Note created {note_id}".format(note_id=id))
            return new_note

        except IntegrityError as e:
            logger.error("Error occured during note creating {e}".format(e=e))
            raise HTTPException(status_code=400, detail="Something went wrong")
        except Exception as e:
            logger.error("Error that is not connected with DB occured during note creating {e}".format(e=e))
            raise HTTPException(status_code=400, detail="Something went wrong")


    async def get_users_note(self, current_user: User, id: uuid.UUID) -> Note:
        for note in current_user.notes:
            if note.id == id:
                return note
        logger.error(
            "User've tried to access notes of another user it can be an attack"
        )
        raise HTTPException(status_code=403, detail="Has no permissions")

    async def get_users_notes(self, user: User) -> List[Note]:
        return user.notes

    async def get_notes_by_tag(self, user: User, tags: List[str]) -> List[Note]:
        return await self.repository.get_by_tags(user_id=user.id, tags=tags)

    async def update_note(
        self, id: str, note_schema: NoteForUpdate, user: User
    ) -> Note:
        for note in user.notes:
            if note.id == id:
                try:
                    updates = note_schema.model_dump(exclude_none=True)
                    note = await self.repository.update(id=id, updates=updates)
                    await self.session.commit()
                    logger.debug("Note updated {note_id}".format(note_id=id))
                    return note
                except IntegrityError as e:
                    logger.error("Error occured during note updating {e}".format(e=e))
                    raise HTTPException(status_code=400, detail="Something went wrong")
        raise HTTPException(status_code=403, detail="Has no permissions")

    async def delete_note(self, id: uuid.UUID, user: User) -> Note:
        for note in user.notes: 
            logger.error(note.id, id)
            if note.id == id:
                note_id = await self.repository.delete(id=id)
                await self.session.commit()
                logger.error("Note deleted {note_id}".format(note_id=id))
                return note_id
            

        logger.error(
            "User've tried to access notes of another user it can be an attack"
        )
        raise HTTPException(status_code=403, detail="Has no permissions")
