from src.authorization.authorization import hash_password
from src.domain.schemas import UserOnAuth
from typing import Annotated
from fastapi import Depends
from src.config import logger


# хэширует пароль до входа в эндпоинт
async def hash(user: UserOnAuth) -> UserOnAuth:
    logger.debug("Password hashed")
    user.password = await hash_password(raw_password=user.password)
    return user


user_with_hashed_password = Annotated[UserOnAuth, Depends(hash)]
