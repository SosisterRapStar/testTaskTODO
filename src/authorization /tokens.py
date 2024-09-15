from datetime import timedelta, datetime
from typing import Any
from jose import jwt
from jose.exceptions import ExpiredSignatureError, j
from src.config import settings
from fastapi import HTTPException



async def create_token(user_data: dict[str, Any], expiration_time: timedelta) -> str:
    payload = user_data.copy()
    expire_in = datetime.now() + expiration_time
    payload["iat"] =  datetime.now()
    payload["exp"] = expire_in
    token = jwt.encode(
        payload,
        settings.security.jwt_secret,
        algorithms=settings.security.jwt_algo,
    )
    return token


async def get_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.security.jwt_secret,
            algorithms=settings.security.jwt_algo,
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Signature has expired')
    
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    
    
    