from datetime import timedelta, datetime
from typing import Any
from jose import jwt
from jose.exceptions import ExpiredSignatureError, j
from src.config import settings
from fastapi import HTTPException
from passlib.context import CryptContext
from .exceptions import PasswordVerificationError

from dataclasses import dataclass


@dataclass
class Authorzation:
    crypt_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    token_settings: dict[str, Any] = {
        "access_token": {
            "expire_time": timedelta(
                minutes=settings.security_settings.ACCES_TOKEN_EXPIRE_MINUTES
            ),
        },
        "refresh_token": {
            "expire_time": timedelta(
                minutes=settings.security_settings.REFRESH_TOKEN_EXPIRE_MINUTES
            ),
        },
    }
    __REFRESH_EXPIRE_TIME = timedelta()

    async def __create_token(
        self, user_data: dict[str, Any], type: str
    ) -> str:
        payload = user_data.copy()
        expire_in = datetime.now() + self.token_settings[type]["expire_time"]
        payload["iat"] = datetime.now()
        payload["exp"] = expire_in
        payload["sub"] = type
        
        token = jwt.encode(
            payload,
            settings.security.jwt_secret,
            algorithms=settings.security.jwt_algo,
        )
        return token

    async def __get_token_payload(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.security.jwt_secret,
                algorithms=settings.security.jwt_algo,
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")

        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    # хэшированный пароль должен поступать из базы данных
    async def check_passwords(self, raw_password: str, hashed_password: str) -> None:
        if not self.crypt_context.verify(raw_password, hashed_password):
            raise PasswordVerificationError

    async def hash_password(self, raw_password: str) -> str:
        return self.crypt_context.hash(raw_password)
