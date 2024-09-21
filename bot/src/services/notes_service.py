from dataclasses import dataclass
from abc import ABC, abstractmethod
from types import TracebackType
from src.backend_client import AbstractAPIClient
from src.schemas import NoteToCreate, Tag, NoteFromBackend, NoteForUpdate
from typing import List
from src.backend_client import AuthorizationError
from src.redis_client import RedisClient
from pydantic import TypeAdapter
from schemas import TokenResponse
from contextlib import AbstractAsyncContextManager
from typing import Coroutine, Any, _T_co
from functools import wraps


@dataclass
class AbstractNotesService(ABC, AbstractAsyncContextManager):
    api_client: AbstractAPIClient
    redis_client: RedisClient
    @abstractmethod
    async def __aenter__(self) -> Coroutine[Any, Any, _T_co]:
        return await super().__aenter__()
    @abstractmethod
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        return await super().__aexit__(exc_type, exc_value, traceback)
    
    @abstractmethod
    async def get_my_notes(self, user_id: str) -> List[NoteFromBackend]:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, note_data: dict) -> None:
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
class NotesService(AbstractNotesService, AbstractAsyncContextManager):
    tokens: TokenResponse | None = None
    user_id: str | None = None


    def __refresh_on_401(func):
        @wraps(func)
        async def wrapper(self: NotesService, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except AuthorizationError:
                try:
                    refreshed_tokens = await self.api_client.refresh_token(refresh_token=self.tokens.refresh_token)
                    self.tokens = refreshed_tokens
                    
                    await self.redis_client.set_object(
                        key=f"{self.user_id}:tokens", 
                        object=refreshed_tokens.model_dump(), 
                        xx=True
                    )
                    
                    return await func(self, *args, **kwargs)
                except AuthorizationError as e:
                    raise e
        return wrapper

    
    async def __aenter__(self):
        if tokens_from_cache := self.__get_user_tokens(self.user_id):
            if not tokens_from_cache:
                raise AuthorizationError
            self.tokens = TokenResponse.model_validate_json(tokens_from_cache)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_resources()

    @__refresh_on_401
    async def __get_user_tokens(self) -> TokenResponse:
        if tokens := await self.redis_client.get_object(key=f"{self.user_id}:tokens"):
            return TokenResponse.model_validate_json(tokens)
        
    @__refresh_on_401
    async def get_note(self) -> NoteFromBackend:
        if note := await self.redis_client.get_object(f"{self.user_id}:{note_id}"):
            return NoteFromBackend.model_validate_json(note)
        else:
            return await self.api_client.get_note(note_id=note_id, token=self.tokens.access_token)
        
    @__refresh_on_401
    async def get_my_notes(self) -> List[NoteFromBackend]:
        if notes := await self.redis_client.get_list(
            key=f"{self.user_id}:notes"
        ):  # ключ notes хранит только id заметок, а не сами заметки
            return_notes = []
            for note_id in notes:
                note = await self.redis_client.get_object(
                    key=f"{self.user_id}:{note_id}"
                )  # взятие кэшированного значения из конеретного ключа
                return_notes.append(NoteFromBackend.model_validate_json(note))
            return notes
        notes = await self.api_client.get_users_notes(token=self.tokens.access_token)

        notes_id = []
        for note in notes:
            notes_id.append(note.id)
            await self.redis_client.set_object(key=f"{self.user_id}:{note.id}")
        await self.redis_client.set_list(key=f"{self.user_id}:notes", values=notes_id)
        return notes
    
    @__refresh_on_401
    async def create_note(self, note_data: dict) -> None:

        note = NoteToCreate(
            title=note_data["title"],
            tags=[Tag(name=tag) for tag in note_data["tags"]],
            content=note_data["content"],
        )

        note_id = await self.api_client.create_note(note=note, token=self.tokens.acce)
        await self.redis_client.set_object(key=f"{self.user_id}:{note_id}", data=note_data)
        await self.redis_client.add_to_list(key=f"{self.user_id}:notes", value=note.id)


    @__refresh_on_401
    async def change_note(self, new_data: dict) -> NoteFromBackend:
        note = NoteForUpdate(**new_data)
        updated_note = await self.api_client.update_note(
            updated_note=note, token=self.tokens.access_token
        )
        await self.redis_client.set_object(
            key=f"{self.user_id}:{updated_note.id}", data=updated_note.model_dump()
        )
        return updated_note
    
    @__refresh_on_401
    async def delete_note(self, note_id: str) -> None:
        deleted_note_id = await self.api_client.delete_note(
            note_id=note_id, token=self.tokens.access_token
        )
        if await self.redis_client.get_object(key=f"{self.user_id}:{deleted_note_id}"):
            await self.redis_client.delete_key(key=f"{self.user_id}:{deleted_note_id}")
        if notes := await self.redis_client.get_list(key=f"{self.user_id}:notes"):
            if deleted_note_id in notes:
                notes.remove[deleted_note_id]
            await self.redis_client.set_list(key=f"{self.user_id}:notes", values=notes)

    @__refresh_on_401
    async def __from_list_to_notes(
        self, notes_id: list[str]
    ) -> List[NoteFromBackend]:
        notes = []
        for note_id in notes_id:
            if note := await self.redis_client.get_object(key=f"{self.user_id}:{note_id}"):
                notes.append(NoteFromBackend.model_validate_json(note))
            raise CacheIsNotConsistent
        
    @__refresh_on_401
    async def find_nodes_by_tags(
        self, tags: List[str]
    ) -> List[NoteFromBackend]:
        try:
            finded_notes = []
            if notes_id := self.redis_client.get_list(key=f"{self.user_id}:notes"):
                notes = self.__from_list_to_notes(user_id=self.user_id, notes_id=notes_id)
            for note in notes:
                if tags in note.tags:
                    finded_notes.append(note)
            return finded_notes

        except CacheIsNotConsistent as e:
            notes = await self.api_client.get_note_using_tags(
                tags=tags, token=self.tokens.access_token
            )
            notes_id = []
            for note in notes:
                notes_id.append(note.id)
                await self.redis_client.set_object(
                    key=f"{self.user_id}:{note.id}", data=note.model_dump_json()
                )
            await self.redis_client.set_list(key=f"{self.user_id}:notes", values=notes_id)
            return notes
