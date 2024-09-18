from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.backend_client import AbstractAPIClient


@dataclass
class AbstractAuthService(ABC):
    api_client: AbstractAPIClient

    @abstractmethod
    async def authorize_user():
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
