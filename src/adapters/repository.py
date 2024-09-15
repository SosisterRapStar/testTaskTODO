from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AbstractRepo(ABC):

    @abstractmethod
    async def create(self):
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self):
        raise NotImplementedError
    
    @abstractmethod
    async def update(self):
        raise NotImplementedError
