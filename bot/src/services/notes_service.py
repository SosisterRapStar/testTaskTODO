from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.backend_client import AbstractAPIClient


@dataclass
class AbstractNotesService(ABC):
    api_client: AbstractAPIClient

    @abstractmethod
    async def get_my_notes():
        pass

    @abstractmethod
    async def add_tag():
        pass

    @abstractmethod
    async def create_note():
        pass

    @abstractmethod
    async def change_note():
        pass

    @abstractmethod
    async def find_nodes_by_tags():
        pass


@dataclass
class NotesService(AbstractNotesService):
    async def get_my_notes(self):
        token = ...
        return await self.api_client.get_users_notes(token=token)
    
    async def add_tag(self, tag_name: str, message: str):
        pass

    async def create_note(self, note_data: str):
        pass

    async def change_note(self):
        pass

    async def find_nodes_by_tags(self):
        pass
        
    

