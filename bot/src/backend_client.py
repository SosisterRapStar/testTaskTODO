from dataclasses import dataclass
from aiogram.client.session.aiohttp import AiohttpSession
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import aiohttp
from src.config import settings
from src.schemas import NoteFromBackend, Tag, TokenResponse, UserData, NoteToCreate, NoteForUpdate
from typing import AsyncGenerator

base_endpoint = settings.backend_url
api_version = "api/v1/"
endpoints = {
    'notes': '/',
    'auth': 'login',
}

@dataclass
class AbstractAPIClient(ABC):
    @abstractmethod
    async def get_users_notes():
        pass

    @abstractmethod
    async def authorization():
        pass

    @abstractmethod
    async def create_note():
        pass

    @abstractmethod
    async def delete_note():
        pass

    @abstractmethod
    async def update_note():
        pass

class APIClient(AbstractAPIClient):
    
    @asynccontextmanager
    async def __get_client(self) -> AsyncGenerator[aiohttp.ClientSession, None]: 
        async with aiohttp.ClientSession() as client:
            yield client

    async def get_users_notes(self):
        async with self.__get_client() as client:
            response = await client.get(base_endpoint + api_version + endpoints['notes'])
            if response.status == 401:
                raise ...
            return NoteFromBackend.model_validate_json(response.json())
        
    async def authorization(self, user_data: UserData):
        async with self.__get_client() as client:
            response = await client.post(url=base_endpoint + api_version + endpoints['auth'],
                        data=user_data.model_dump())
            if response.status == 401:
                raise ... 
            return TokenResponse.model_validate_json(response.json())
        
    async def create_note(self, note: NoteToCreate):
        async with self.__get_client() as client:
            response = await client.post(url=base_endpoint + api_version + endpoints['notes'],
                        data=note.model_dump())
            if response.status == 401:
                raise ... 
            return TokenResponse.model_validate_json(response.json())
        
    async def delete_note(self, note_id: str):
        async with self._get_client() as client:
            response = await client.delete(url=base_endpoint+api_version+endpoints['notes'] + note_id)
            if response.status == 401:
                raise ... 
            return response.text()
        
    async def update_note(self, updated_note: NoteForUpdate):
        async with self._get_client() as client:
            response = await client.delete(url=base_endpoint+api_version+endpoints['notes'] + str(updated_note.id))
            if response.status == 401:
                raise ... 
            return response.text()
        
        
    