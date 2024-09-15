from datetime import timedelta, datetime
from typing import Any

from jose import jwt


from src.config import settings



async def create_token(user_data: dict[str, Any], expiration_time: timedelta):
    payload = user_data.copy()
    expire_in = datetime.now() + expire
    payload.update({"iat": datetime.now(), "exp": expire_in})
    return payload