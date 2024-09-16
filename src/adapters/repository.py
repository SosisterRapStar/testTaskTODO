from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List, ClassVar
from src.domain.orm import Base
from src.domain.entities import Note, User
from dataclasses import dataclass

@dataclass
class AbstractAlchemyRepo(ABC):
    session: AsyncSession
    _model: ClassVar[Type[Base]] = None

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

    @abstractmethod
    async def get_list(self, *args, **kwargs) -> Base:
        raise NotImplementedError

@dataclass
class AbstractNotesRepo(AbstractAlchemyRepo):
    _model = Note
    @abstractmethod
    async def create(self, title: str, tags: List[str]):
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, id: str):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: str, updates: dict):
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: str):
        raise NotImplementedError

    @abstractmethod
    async def get_by_tags(self, tags: List[str]):
        raise NotImplementedError
    
@dataclass
class AbstractUserRepo(AbstractAlchemyRepo):
    _model = User

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
    



    