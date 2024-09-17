from typing import Annotated
from fastapi import Request, Depends
from starlette.datastructures import Headers
from src.adapters.repository import UserRepo
from fastapi import HTTPException
from .db_services import session_dep
from src.authorization.authorization import get_token_payload, Authorzation
from sqlalchemy.exc import NoResultFound
from src.domain.entities import User
from src.config import logger


async def _get_auth_user(request: Request, session: session_dep) -> User:
    user_id = await _get_user_id(scope=request.scope)
    user_repo = UserRepo(session=session)  # вынести как зависимость
    try:
        user = await user_repo.get(id=user_id)
        logger.debug("User has been authorized {user_name}".format(user_name=user.name))
        return user
    except NoResultFound:
        logger.warning(
            "It seems that user try to log in with very outdated JWT it can be an attack"
        )
        raise HTTPException(status_code=401, detail="Invalid token")


async def _get_user_id(scope) -> str:
    headers = Headers(scope=scope)
    payload = await get_token_payload(await _token_in_headers(headers=headers))
    if payload["sub"] != "access_token":
        logger.warning(
            "It seems that user try to log in with WRONG JWT it can be an attack"
        )
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload["id"]
    return user_id


async def _token_in_headers(headers) -> str:
    try:
        auth_header = headers["Authorization"]
    except LookupError:
        raise HTTPException(status_code=401, detail="Non authorized user")
    try:
        token_type, token = auth_header.split()
        assert token_type == "Bearer"
    except Exception as e:
        logger.warning("Wrong headers provided for auth type")
        raise HTTPException(status_code=401, detail="Invalid token")
    return token


async def _get_authorization_service(session: session_dep) -> Authorzation:
    return Authorzation(user_repo=UserRepo(session=session), user_data=None)


get_auth_service = Annotated[Authorzation, Depends(_get_authorization_service)]
get_auth_user = Annotated[User, Depends(_get_auth_user)]
