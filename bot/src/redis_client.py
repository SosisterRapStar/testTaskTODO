import redis.asyncio as redis
import asyncio
from redis import Redis
from src.config import settings
from dataclasses import dataclass
import json


class RedisManager:
    pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        max_connections=settings.redis_max_pool_size,
        decode_responses=True,
    )

    @classmethod
    def get_connection(cls) -> Redis:
        return redis.Redis.from_pool(connection_pool=cls.pool)


@dataclass
class RedisClient:
    redis: Redis = RedisManager.get_connection

    async def set_object(self, key: str, data: dict, **kwargs) -> None:
        json_string = json.dumps(data)
        async with self.redis as r:
            await r.set(key, json_string, **kwargs)

    async def set_list(self, key: str, values: list[dict] | list[str]) -> None:
        async with self.redis as r:
            for value in values:
                await r.rpush(key, json.dumps(value))

    async def add_to_list(self, key: str, value: str) -> None:
        async with self.redis as r:
            await r.rpush(key, json.dumps(value))

    async def get_object(self, key: str) -> str:
        async with self.redis as r:
            return await r.get(key)

    async def get_list(self, key: str) -> list[str] | None:
        async with self.redis as r:
            res = await r.lrange(key, 0, -1)
            if res is not None:
                return res
            return None

    async def delete_key(self, key: str) -> str:
        async with self.redis as r:
            await r.delete(key)
        return key
