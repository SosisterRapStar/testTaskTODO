from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.backend_client import AbstractAPIClient
from src.schemas import UserData, TokenResponse
from src.redis_client import RedisClient
from src.backend_client import AuthorizationError, InvalidData
import json
from src.config import logger

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
        """

        Args:
            user_id (str): user_id

        Raises:
            AuthorizationError: rased by api client when it gets 401 status code from backend

        Returns:
            TokenResponse: pydantic token model
        """
        
        if tokens := await self.redis_client.get_object(key=f"{user_id}:tokens"):
            logger.debug("Getting tokens from redis")
            return TokenResponse.model_validate_json(tokens)
        else:
            raise AuthorizationError

    async def authorize_user(self, name: str, password: str, user_id: str) -> None:
        user_data = UserData(name=name, password=password)
        tokens: TokenResponse = await self.api_client.authorization(user_data=user_data)
        await self.redis_client.set_object(
            key=f"{user_id}:tokens", data=tokens.model_dump(), ex=tokens.expires_in
        )

    async def refresh_tokens(self, user_id: str) -> TokenResponse:
        """
        Refreshs user tokens

        Args:
            user_id (str): user_id

        Returns:
            TokenResponse: pydantic token model
        """
        logger.debug("Refreshing tokens")
        tokens = await self.get_user_tokens(user_id=user_id)
        refreshed_tokens = await self.api_client.refresh_token(
            refresh_token=tokens.refresh_token
        )
        tokens = refreshed_tokens

        await self.redis_client.set_object(
            key=f"{user_id}:tokens", data=refreshed_tokens.model_dump(), xx=True
        )
        # xx параметр не обновляет ttl, обновляет ключ только если таковой существует
        # не должно вернуть none, если вернет то сначал получим auth error из api_client
        return tokens
