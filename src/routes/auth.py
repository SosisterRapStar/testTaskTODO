from fastapi import APIRouter, Header, HTTPException
from typing import Annotated
from starlette import status
from dependencies.auth_deps import get_auth_service
from dependencies.db_services import user_service
from dependencies.hash_dep import user_with_hashed_password
from src.domain.schemas import UserOnResponse, UserOnAuth
from src.authorization.schemas import TokenResponse

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserOnResponse)
async def registration(
    user_service: user_service, user_schema: user_with_hashed_password
):
    print(user_schema.name)
    return await user_service.register_user(user=user_schema)
    # return {"message": "user_created"}


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def authorization(auth_service: get_auth_service, user_schema: UserOnAuth):
    auth_service.set_user_info(user=user_schema)
    return await auth_service.get_token()


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: Annotated[str | None, Header()], auth_service: get_auth_service
):
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="No valid haeders",
        )
    return await auth_service.update_access_token(refresh_token=refresh_token)
