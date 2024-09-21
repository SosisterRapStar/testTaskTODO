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
    async def get_user_tokens(self, user_id: str) -> TokenResponse:
        raise NotImplementedError

    @abstractmethod
    async def authorize_user(self, name: str, password: str, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def refresh_tokens(self, user_id: str) -> TokenResponse:
        raise NotImplementedError


@dataclass
class AuthService(AbstractAuthService):
    async def get_user_tokens(self, user_id: str) -> TokenResponse:
        if tokens := await self.redis_client.get_object(key=f"{user_id}:tokens"):
            return TokenResponse.model_validate_json(tokens)
        else:
            raise AuthorizationError

    async def authorize_user(self, name: str, password: str, user_id: str) -> None:
        user_data = UserData(name=name, password=password)
        tokens: TokenResponse = await self.api_client.authorization(user_data=user_data)
        await self.redis_client.set_object(key=f"{user_id}:tokens", data=tokens.model_dump())

    async def refresh_tokens(self, user_id: str) -> TokenResponse:
        tokens = await self.get_user_tokens(user_id=user_id)
        refreshed_tokens = await self.api_client.refresh_token(refresh_token=tokens.refresh_token)
        tokens = refreshed_tokens
                    
        await self.redis_client.set_object(
            key=f"{self.user_id}:tokens", 
            object=refreshed_tokens.model_dump(), 
            xx=True
        )
        return tokens
                    
        
