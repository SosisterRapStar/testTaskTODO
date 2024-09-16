from src.authorization.authorization import hash_password
from src.domain.schemas import UserOnAuth
from typing import Annotated
from fastapi import Depends


# хэширует пароль до входа в эндпоинт
async def hash(user: UserOnAuth) -> UserOnAuth:
    user.password = await hash_password(raw_password=user.password)
    return user


user_with_hashed_password = Annotated[UserOnAuth, Depends(hash)]
