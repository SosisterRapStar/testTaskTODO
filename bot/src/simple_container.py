from dataclasses import dataclass
from backend_client import AbstractAPIClient
from src.services.notes_service import AbstractNotesService
from src.backend_client import APIClient
from src.services.notes_service import NotesService
from aiogram import Bot
from src.config import settings
from aiogram.fsm.storage.redis import RedisStorage
from src.redis_client import RedisClient, RedisManager


@dataclass
class NaiveSimpleDIContainer:
    api_client: AbstractAPIClient
    # auth_service: AbstractAuthService
    notes_service: AbstractNotesService
    bot: Bot
    storage: RedisStorage


container = NaiveSimpleDIContainer(
    notes_service=NotesService(api_client=APIClient, redis_client=RedisClient()),
    api_client=APIClient(),
    bot=Bot(token=settings.api_key),
    storage=RedisStorage.from_url("redis://localhost:6379"),
)
