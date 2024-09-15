from dataclasses import dataclass
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List, ClassVar
from src.domain.orm import Base


@dataclass
class AbstractRepo(ABC):
    session: AsyncSession
    _model: ClassVar[Type[Base]] = None

    @abstractmethod
    async def create(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError

    @abstractmethod
    async def update(self):
        raise NotImplementedError

    @abstractmethod
    async def get(self):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self):
        raise NotImplementedError


@dataclass
class AbstractNotesRepo(AbstractRepo):
    @abstractmethod
    async def get_by_tags(self):
        raise NotImplementedError


@dataclass
class AbstractUserRepo(AbstractRepo):
    pass
