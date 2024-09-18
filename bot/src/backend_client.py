from dataclasses import dataclass
from aiogram.client.session.aiohttp import AiohttpSession
from abc import ABC, abstractmethod

@dataclass
class AbstractAPIClient(ABC):
    session: AiohttpSession

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

    