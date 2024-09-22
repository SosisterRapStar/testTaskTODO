from dataclasses import dataclass
from abc import ABC, abstractmethod
from types import TracebackType
from src.backend_client import AbstractAPIClient
from src.schemas import NoteToCreate, Tag, NoteFromBackend, NoteForUpdate
from typing import List
from src.backend_client import AuthorizationError
from src.redis_client import RedisClient
from functools import wraps
from src.services.auth_service import AbstractAuthService
from src.config import logger
import json

@dataclass
class AbstractNotesService(ABC):
    api_client: AbstractAPIClient
    redis_client: RedisClient
    auth_service: AbstractAuthService

    @abstractmethod
    async def get_my_notes(self, user_id: str) -> List[NoteFromBackend]:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, note_data: dict, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def change_note(self, new_data: dict, user_id: str):
        raise NotImplementedError

    @abstractmethod
    async def find_nodes_by_tags(
        self, user_id: str, tags: List[str]
    ) -> List[NoteFromBackend]:
        raise NotImplementedError

    @abstractmethod
    async def delete_note(self, note_id: str, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_note(self, note_id: str, user_id: str) -> NoteFromBackend:
        raise NotImplementedError


@dataclass
class CacheIsNotConsistent(Exception):
    message: str

    def __str__(self) -> str:
        return "Cache is not consistent err"


@dataclass
class NotesService(AbstractNotesService):
    def __refresh_on_401(func):
        @wraps(func)  # нужно чтобы сохранить метадату функции
        async def wrapper(self: "NotesService", user_id: str, *args, **kwargs):
            try:
                return await func(self, user_id=user_id, *args, **kwargs)  # просто вызываем функцию
            except AuthorizationError:
                await self.auth_service.refresh_tokens(user_id=user_id)  # обновялем токены
                return await func(self, user_id=user_id, *args, **kwargs)

        return wrapper

    @__refresh_on_401
    async def get_note(self, note_id: str, user_id: str) -> NoteFromBackend:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        if note := await self.redis_client.get_object(f"{user_id}:{note_id}"):
            return NoteFromBackend.model_validate_json(note)
        else:
            return await self.api_client.get_note(
                note_id=note_id, token=tokens.access_token
            )

    @__refresh_on_401
    async def get_my_notes(self, user_id: str) -> List[NoteFromBackend]:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        if notes := await self.redis_client.get_list(
            key=f"{user_id}:notes"
        ):  # ключ notes хранит только id заметок, а не сами заметки
            logger.debug("Notes got from cache")
            return_notes = []
            for note_id in notes:
                note = await self.redis_client.get_object(
                    key=f"{user_id}:{note_id}"
                )  # взятие кэшированного значения из конеретного ключа
                print(note)
                return_notes.append(NoteFromBackend.model_validate_json(note))
            return return_notes
        logger.debug("Notes got from api")
        notes = await self.api_client.get_users_notes(token=tokens.access_token)
        notes_id = []
        for note in notes:
            notes_id.append(note.id)
            await self.redis_client.set_object(key=f"{user_id}:{note.id}", data=note.model_dump())
        await self.redis_client.set_list(key=f"{user_id}:notes", values=notes_id)
        return notes

    @__refresh_on_401
    async def create_note(self, note_data: dict, user_id: str) -> None:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)

        note = NoteToCreate(
            title=note_data["title"],
            tags=[Tag(name=tag) for tag in note_data["tags"]],
            content=note_data["content"],
        )
        note = await self.api_client.create_note(note=note, token=tokens.access_token)
        await self.redis_client.set_object(key=f"{user_id}:{note.id}", data=note.model_dump())
        await self.redis_client.add_to_list(key=f"{user_id}:notes", value=note.id)
        logger.debug("New note has been created")
        return note

    @__refresh_on_401
    async def change_note(self, new_data: dict, user_id: str) -> NoteFromBackend:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        note = NoteForUpdate.model_validate_json(json.dumps(new_data))
        updated_note = await self.api_client.update_note(
            updated_note=note, token=tokens.access_token
        )
        await self.redis_client.set_object(
            key=f"{user_id}:{updated_note.id}", data=updated_note.model_dump()
        )
        logger.debug("Note has been updated")
        return updated_note

    @__refresh_on_401
    async def delete_note(self, note_id: str, user_id: str) -> None:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        deleted_note_id = await self.api_client.delete_note(
            note_id=note_id, token=tokens.access_token
        )
        print("Deleting note", deleted_note_id, user_id)

        if note := await self.redis_client.get_object(key=f"{user_id}:{deleted_note_id}"):
            print(note)
            await self.redis_client.delete_key(key=f"{user_id}:{deleted_note_id}")
        if notes := await self.redis_client.get_list(key=f"{user_id}:notes"):
            await self.redis_client.remove_from_list(key=f"{user_id}:notes", value=deleted_note_id)

    @__refresh_on_401
    async def __from_list_to_notes(
        self, notes_id: list[str], user_id: str
    ) -> List[NoteFromBackend]:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        notes = []
        for note_id in notes_id:
            if note := await self.redis_client.get_object(key=f"{user_id}:{note_id}"):
                notes.append(NoteFromBackend.model_validate_json(note))
            raise CacheIsNotConsistent

    @__refresh_on_401
    async def find_nodes_by_tags(
        self, tags: List[str], user_id: str
    ) -> List[NoteFromBackend]:
        tokens = await self.auth_service.get_user_tokens(user_id=user_id)
        try:
            finded_notes = []
            if notes_id := self.redis_client.get_list(key=f"{user_id}:notes"):
                notes = self.__from_list_to_notes(user_id=user_id, notes_id=notes_id)
            for note in notes:
                if tags in note.tags:
                    finded_notes.append(note)
            return finded_notes

        except CacheIsNotConsistent as e:
            notes = await self.api_client.get_note_using_tags(
                tags=tags, token=tokens.access_token
            )
            notes_id = []
            for note in notes:
                notes_id.append(note.id)
                await self.redis_client.set_object(
                    key=f"{user_id}:{note.id}", data=note.model_dump_json()
                )
            await self.redis_client.set_list(key=f"{user_id}:notes", values=notes_id)
            return notes
