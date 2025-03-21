from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List, ClassVar
from src.domain.orm import Base
from src.domain.entities import Note, User, Tag, NoteTagSecondary
from sqlalchemy import Result, select, delete, update, func
from dataclasses import dataclass
import uuid
from sqlalchemy.exc import IntegrityError
from src.config import logger


@dataclass
class AbstractAlchemyRepo(ABC):
    session: AsyncSession

    @abstractmethod
    async def create(self, *args, **kwargs) -> Base:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> Base:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs) -> Base:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *args, **kwargs) -> Base:
        raise NotImplementedError


@dataclass
class AbstractNotesRepo(AbstractAlchemyRepo):
    @abstractmethod
    async def create(self, title: str, tags: List[str], content: str) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: str, updates: dict) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: str) -> Note:
        raise NotImplementedError

    @abstractmethod
    async def get_by_tags(self, tags: List[str], user_id: str) -> Note:
        raise NotImplementedError


@dataclass
class NotesRepo(AbstractNotesRepo):
    async def create(self, title: str, tags: List[str], user_id: str, content: str) -> Note:
        user_id = uuid.UUID(user_id)
        new_note = Note(title=title, content=content)
        self.session.add(new_note)
        for tag_name in tags:
            tag = await self.session.scalar(select(Tag).where(Tag.name == tag_name))
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)

            new_note.tags.append(tag)
        new_note.user_fk = user_id
        return new_note

    async def get(self, note_id: str) -> Note:
        stmt = select(Note).where(Note.id == id)
        return await self.session.scalar(statement=stmt)

    async def delete(self, id: uuid.UUID) -> Result:
        stmt = delete(Note).where(Note.id == id).returning(Note.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update(self, id: uuid.UUID, updates: dict) -> Note | Result:
        new_tags = updates.pop("tags", None)
        note = await self.session.scalar(select(Note).where(Note.id == id))
        logger.debug(new_tags)

        if new_tags:
            new_tag_names = set([tag["name"] for tag in new_tags])
            logger.debug(f"new_tags_names {new_tag_names}")
            no_need_to_check = set()
            tags_to_remove = []
            for old_tag in note.tags:
                logger.debug(f"old tag in sycle {old_tag.name}, {old_tag.id}")
                if old_tag.name not in new_tag_names:
                    logger.debug(f" tag to remove {old_tag.name}")
                    tags_to_remove.append(old_tag)
                else:
                    no_need_to_check.add(old_tag.name)

            for i in tags_to_remove:
                note.tags.remove(i)

            for new_tag in new_tag_names:
                if new_tag not in no_need_to_check:
                    tag = await self.session.scalar(
                        select(Tag).where(Tag.name == new_tag)
                    )
                    if tag is None:
                        tag = Tag(name=new_tag)
                        self.session.add(tag)
                    note.tags.append(tag)

            await self.__delete_tag_orphans(self.session)

        for key, value in updates.items():
            setattr(note, key, value)
        return note

    async def get_by_tags(self, user_id: uuid.UUID, tags: List[str]) -> List[Note]:
        stmt = (
            select(Note)
            .join(NoteTagSecondary, Note.id == NoteTagSecondary.note_id)
            .where((Tag.name.in_(tags)) & (Note.user_fk == user_id))
        )
        result = await self.session.execute(stmt)
        result = result.unique()
        return list(result.scalars().all())

    async def __delete_tag_orphans(self, session: AsyncSession):
        """
        Функция, которая удаляет никем не занятые теги
        """

        await session.execute(delete(Tag).where(~Tag.notes.any()))

        logger.debug("Orphaned tags deleted.")


@dataclass
class AbstractUserRepo(AbstractAlchemyRepo):
    @abstractmethod
    async def create(self, name: str, password: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: str, updates: dict) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def has_note(self, note_id: str) -> bool:
        raise NotImplemented


@dataclass
class UserRepo(AbstractUserRepo):
    async def create(self, name: str, password: str) -> User:
        user = User(name=name, password=password)
        self.session.add(user)
        return user

    async def delete(self, id: str) -> Result:
        id = uuid.UUID(id)
        stmt = delete(User).where(User.id == id).returning(User.name)
        return await self.session.execute()

    async def update(self, id: str, updates: dict) -> Result:
        stmt = update(User).where(User.id == id).values(updates).returning(User)
        res = await self.session.execute(stmt)
        return res

    async def get(self, id: str) -> User:
        id = uuid.UUID(id)
        stmt = select(User).where(User.id == id)
        user = await self.session.scalar(statement=stmt)
        await user.awaitable_attrs.notes
        return user

    async def has_note(self, user_id: str, note_id: str) -> bool:
        user_id = uuid.UUID(user_id)
        note_it = uuid.UUID(note_id)
        stmt = select(Note).where(Note.user_fk == user_id and Note.id == note_id)
        if not await self.session.scalar(statement=stmt):
            return False
        return True

    async def get_by_name(self, name: str) -> User:
        stm = select(User).where(User.name == name)
        res = await self.session.execute(stm)
        return res.scalar_one()
