from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Response

from app.api.schemas.user import (
    UserCreateRequest,
    UserLoginRequest,
    UserRefreshTokenRequest,
)
from app.api.dep.db import DBDep
from app.services.user import UserService
from app.api.api_decorators.user import clear_auth_cookies, set_auth_cookies
from app.exceptions.auth import InvalidTokenException

router = APIRouter()

@router.post("/")
@set_auth_cookies
async def create_user(user: UserCreateRequest, db: DBDep, response: Response):
    return await UserService(db).create_user(user)


@router.post("/login")
@set_auth_cookies
async def login(user: UserLoginRequest, db: DBDep, response: Response):
    return await UserService(db).login(user)


@router.post("/refresh")
@set_auth_cookies
async def refresh_token(
    db: DBDep,
    response: Response,
    token: Annotated[UserRefreshTokenRequest | None, Body()] = None,
    refresh_token_cookie: Annotated[
        str | None,
        Cookie(alias="refresh_token"),
    ] = None,
):
    refresh_token_value = refresh_token_cookie or (token.refresh_token if token else None)
    if refresh_token_value is None:
        raise InvalidTokenException()

    return await UserService(db).refresh_token(
        UserRefreshTokenRequest(refresh_token=refresh_token_value)
    )


@router.post("/logout")
@clear_auth_cookies
async def logout(
    db: DBDep,
    response: Response,
    token: Annotated[UserRefreshTokenRequest | None, Body()] = None,
    refresh_token_cookie: Annotated[
        str | None,
        Cookie(alias="refresh_token"),
    ] = None,
):
    refresh_token_value = refresh_token_cookie or (token.refresh_token if token else None)
    return await UserService(db).logout(
        UserRefreshTokenRequest(refresh_token=refresh_token_value)
    )