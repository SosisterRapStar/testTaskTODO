from dataclasses import dataclass
from abc import ABC


@dataclass
class AbstractRepo(ABC):
    async def create(self):
        raise NotImplementedError

    async def delete(self):
        raise NotImplementedError

    async def update(self):
        raise NotImplementedError
