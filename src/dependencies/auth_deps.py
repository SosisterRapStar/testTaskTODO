from typing import Annotated
from fastapi import Request, Depends
from starlette.datastructures import Headers
from src.adapters.repository import UserRepo
from fastapi import HTTPException
from .db_services import session_dep
from src.authorization.authorization import get_token_payload, Authorzation
from sqlalchemy.orm import NoResultFound
from src.domain.entities import User



async def _get_auth_user(request: Request, session: session_dep) -> User:
    user_id = await _get_user_id(scope=request.scope)
    user_repo = UserRepo(session=session_dep) # вынести как зависимость
    try:
        user = await user.get(id=user_id)

    except NoResultFound:
        raise HTTPException(
            status_code=401, detail="Invalid token"
        )

    return user


async def _get_user_id(scope) -> str:
    headers = Headers(scope=scope)
    payload = get_token_payload(await _token_in_headers(headers=headers))
    user_id = payload["id"]
    return user_id


async def _token_in_headers(headers) -> str:
    try:
        auth_header = headers["Authorization"]
    except LookupError:
        raise HTTPException(status_code=401, details="Non authorized user")
    try:
        token_type, token = auth_header.split()
        assert token_type == "Bearer"
    except Exception as e: # если токен не bearer то выдаем исключение
        raise HTTPException(status_code=401, details="Invalid token")
    return token


async def _get_authorization_service(session: session_dep) -> Authorzation:
    return Authorzation(repo=UserRepo(session=session))

get_auth_service = Annotated[Authorzation, Depends(_get_authorization_service)]
user_service = Annotated[User, Depends(_get_auth_user)]
