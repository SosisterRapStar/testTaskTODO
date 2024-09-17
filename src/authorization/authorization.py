from datetime import timedelta, datetime
from typing import Any
from jose import jwt
from src.config import settings
from fastapi import HTTPException
from passlib.context import CryptContext
from .exceptions import PasswordVerificationError
from adapters.repository import AbstractUserRepo
from dataclasses import dataclass, field
from src.domain.schemas import UserOnAuth
from src.domain.entities import User
from sqlalchemy.exc import NoResultFound
from .schemas import TokenResponse
from src.config import logger


def get_default_settings():
    return {
        "access_token": {
            "expire_time": timedelta(
                minutes=settings.security.access_token_expire_minutes
            ),
        },
        "refresh_token": {
            "expire_time": timedelta(
                minutes=settings.security.refresh_token_expire_minutes
            ),
        },
    }


crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class Authorzation:
    user_repo: AbstractUserRepo
    user_data: dict | None = None

    token_settings: dict[str, Any] = field(default_factory=get_default_settings)

    def set_user_info(self, user: UserOnAuth):
        self.user_data = dict()
        self.user_data["name"] = user.name
        self.user_data["password"] = user.password

    async def get_token(self):
        try:
            user_from_db = await self.user_repo.get_by_name(name=self.user_data["name"])
            await self.check_passwords(
                self.user_data["password"], user_from_db.password
            )

        except PasswordVerificationError:
            raise PasswordVerificationError

        except NoResultFound:
            raise HTTPException(status_code=400, detail="Invalid username or password")

        logger.debug("New jwt token created")
        return await self.__get_user_tokens(user_from_db)

    async def update_access_token(self, refresh_token):
        data = await get_token_payload(refresh_token)
        if data["sub"] != "refresh_token":
            logger.warning(
                "User is trying to refresh token with access token it can be an attack"
            )
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = data["id"]

        try:
            user = await self.user_repo.get(id=user_id)
        except (LookupError, NoResultFound):
            logger.warning("User has provided maybe outdated JWT it can be attack")
            raise HTTPException(status_code=401, detail="Invalid token")

        return await self.__get_user_tokens(user=user, refresh_token=refresh_token)

    async def __get_user_tokens(self, user: User, refresh_token=None):
        data = {"name": user.name, "id": str(user.id)}
        access_token = await self.__create_token(user_data=data, type="access_token")

        if not refresh_token:
            refresh_token = await self.__create_token(
                user_data=data, type="refresh_token"
            )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_settings["access_token"]["expire_time"].seconds,
        )

    async def __create_token(self, user_data: dict[str, Any], type: str) -> str:
        payload = user_data.copy()
        expire_in = datetime.now() + self.token_settings[type]["expire_time"]
        payload["iat"] = datetime.now()
        payload["exp"] = expire_in
        payload["sub"] = type

        token = jwt.encode(
            payload,
            settings.security.jwt_secret,
            algorithm=settings.security.jwt_algo,
        )
        return token

    # хэшированный пароль должен поступать из базы данных
    async def check_passwords(self, raw_password: str, hashed_password: str) -> None:
        if not crypt_context.verify(raw_password, hashed_password):
            logger.warning("User has provided wrong password")
            raise PasswordVerificationError


async def get_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.security.jwt_secret,
            algorithms=settings.security.jwt_algo,
        )
        return payload

    except jwt.JWTError as e:
        logger.warning("User has provided wrong encoded JWT it can be attack")
        raise HTTPException(status_code=401, detail="Invalid token")


async def hash_password(raw_password: str) -> str:
    return crypt_context.hash(raw_password)
