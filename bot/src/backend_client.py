from dataclasses import dataclass
from aiogram.client.session.aiohttp import AiohttpSession
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import aiohttp
from src.config import settings
from src.schemas import (
    NoteFromBackend,
    Tag,
    TokenResponse,
    UserData,
    NoteToCreate,
    NoteForUpdate,
)
from typing import AsyncGenerator, List
from pydantic import TypeAdapter

base_endpoint = settings.backend_url
api_version = "api/v1/"
endpoints = {"notes": "/", "auth": {"token": "login", "refresh": "refresh"}}


@dataclass
class AuthorizationError(Exception):
    message: str

    def __str__(self) -> str:
        return f"User is not authorized {self.message}"


@dataclass
class AbstractAPIClient(ABC):
    @abstractmethod
    async def get_users_notes(self, token: str) -> List[NoteFromBackend]:
        raise NotImplementedError

    @abstractmethod
    async def authorization(self, user_data: UserData) -> TokenResponse:
        raise NotImplementedError

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        raise NotImplementedError

    @abstractmethod
    async def create_note(self, note: NoteToCreate, token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete_note(self, note_id: str, token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def update_note(
        self, updated_note: NoteForUpdate, token: str
    ) -> NoteFromBackend:
        raise NotImplementedError

    @abstractmethod
    async def get_note_using_tags(
        self, tags: List[str], token: str
    ) -> List[NoteFromBackend]:
        raise NotImplementedError

    @abstractmethod
    async def get_note(self, note_id: str, user_id: str) -> NoteFromBackend:
        raise NotImplementedError


class APIClient(AbstractAPIClient):
    @asynccontextmanager
    async def __get_client(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        async with aiohttp.ClientSession() as client:
            yield client

    async def get_users_notes(self, token: str):
        async with self.__get_client() as client:
            response = await client.get(
                url=base_endpoint + api_version + endpoints["notes"],
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            adapter = TypeAdapter(List[NoteFromBackend])
            list_notes = adapter.validate_json(response.json())
            return list_notes

    async def authorization(self, user_data: UserData):
        async with self.__get_client() as client:
            response = await client.post(
                url=base_endpoint + api_version + endpoints["auth"]["token"],
                data=user_data.model_dump(),
            )
            if response.status == 401:
                raise AuthorizationError()
            return TokenResponse.model_validate_json(response.json())

    async def refresh_token(self, refresh_token: str):
        async with self.__get_client() as client:
            response = await client.post(
                url=base_endpoint + api_version + endpoints["auth"]["refresh"],
                headers={"refresh-token": f"{refresh_token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            return TokenResponse.model_validate_json(response.json())

    async def create_note(self, note: NoteToCreate, token: str):
        async with self.__get_client() as client:
            response = await client.post(
                url=base_endpoint + api_version + endpoints["notes"],
                data=note.model_dump(),
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            return response.text()

    async def delete_note(self, note_id: str, token: str):
        async with self._get_client() as client:
            response = await client.delete(
                url=base_endpoint + api_version + endpoints["notes"] + note_id,
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            return response.text()

    async def update_note(
        self, updated_note: NoteForUpdate, token: str
    ) -> NoteFromBackend:
        async with self._get_client() as client:
            response = await client.patch(
                url=base_endpoint
                + api_version
                + endpoints["notes"]
                + str(updated_note.id),
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            return NoteFromBackend.model_validate_json(response.json())

    async def get_note_using_tags(
        self, tags: List[Tag], token: str
    ) -> List[NoteFromBackend]:
        async with self._get_client() as client:
            params = []
            for tag in tags:
                params.append(("tag", tag.name))

            response = await client.delete(
                url=base_endpoint + api_version + endpoints["notes"],
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status == 401:
                raise AuthorizationError()
            adapter = TypeAdapter(List[NoteFromBackend])
            list_notes = adapter.validate_json(response.json())
            return list_notes

    async def get_note(self, note_id: str, token: str) -> NoteFromBackend:
        async with self._get_client() as client:
            response = await client.get(
                url=base_endpoint + api_version + endpoints["notes"] + note_id,
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status == 401:
                raise AuthorizationError()

            return NoteFromBackend.model_validate_json(response.json())
