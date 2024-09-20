from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.backend_client import AbstractAPIClient
from src.schemas import UserData, TokenResponse
from src.redis_client import RedisClient
from src.backend_client import AuthorizationError
import json


@dataclass
class AbstractAuthService(ABC):
    api_client: AbstractAPIClient
    redis_client: RedisClient

    @abstractmethod
    async def authorize_user():
        raise NotImplementedError

    @abstractmethod
    async def refresh_token():
        raise NotImplementedError


@dataclass
class AuthService(AbstractAuthService):
    async def __get_user_tokens(self, user_id: str) -> TokenResponse:
        if tokens := await self.redis_client.get_object(key=f"{user_id}:tokens"):
            return TokenResponse.model_validate_json(tokens)
        else:
            raise AuthorizationError

    async def authorize_user(self, name: str, password: str, user_id: str) -> None:
        user_data = UserData(name=name, password=password)
        tokens: TokenResponse = await self.api_client.authorization(user_data=user_data)
        self.redis_client.set_object(key=f"{user_id}:tokens", data=tokens.model_dump())

    async def refresh_token(self, user_id: str) -> None:
        tokens = await self.__get_user_tokens(user_id=user_id)
        tokens_in_dict = json.loads(tokens)
        tokens = await self.api_client.refresh_token(
            refresh_token=tokens_in_dict["refresh_token"]
        )
        await self.redis_client.set_list(
            key=f"{user_id}:tokens", data=tokens.model_dump()
        )
