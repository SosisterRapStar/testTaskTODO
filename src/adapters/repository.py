from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List, ClassVar
from src.domain.orm import Base
from src.domain.entities import Note, User, Tag, NoteTagSecondary
from sqlalchemy import Result, select, delete, update, func
from dataclasses import dataclass
import uuid


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
    async def create(self, title: str, tags: List[str]) -> Note:
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

    async def create(self, title: str, tags: List[str], user_id: str) -> Note:
        user_id = uuid.UUID(user_id)
        new_note = Note(title=title)
        self.session.add(new_note)
        await new_note.awaitable_attrs.tags
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

    async def delete(self, id: str) -> Result:
        id = uuid.UUID(id)
        stmt = delete(Note).where(Note.id == id).returning(Note.title)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update(self, id: str, updates: dict) -> Note | Result:
        id = uuid.UUID(id)
        new_tags = updates.pop("tags", None)
        note = await self.session.scalar(select(Note).where(Note.id == id))

        if new_tags:
            await note.awaitable_attrs.tags
            old_tags = note.tags
            no_need_to_check = set()
            for old_tag in new_tags:
                if old_tag not in new_tags:
                    note.tags.pop(old_tag)
                else:
                    no_need_to_check.add(old_tag)

            for new_tag in new_tags:
                if new_tag not in no_need_to_check:
                    tag = await self.session.scalar(
                        select(Tag).where(Tag.name == new_tag)
                    )
                    if not tag:
                        tag = Tag(name=new_tag)
                        self.session.add(tag)
                    note.tags.append(tag)

        for key, value in updates.items():
            setattr(note, key, value)
        return note

    async def get_by_tags(self, user_id: str, tags: List[str]) -> Note:
        id = uuid.UUID(id)
        user_id = uuid.UUID(user_id)
        stmt = (
            select(Note)
            .join(NoteTagSecondary, Note.id == NoteTagSecondary.note_id)
            .where(Tag.name.in_(tags) and Note.user_fk == user_id)
            .group_by(Note.id)
            .having(func.count(Tag.id) == len(tags))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


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
