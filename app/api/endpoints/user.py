from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Response

from app.api.api_decorators.user import clear_auth_cookies, set_auth_cookies
from app.api.dep.db import DBDep
from app.api.schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserRefreshTokenRequest,
    UserRefreshTokenResponse,
)
from app.exceptions.auth import InvalidTokenException
from app.services.user import UserService

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse)
@set_auth_cookies
async def create_user(user: UserCreateRequest, db: DBDep, response: Response):
    return await UserService(db).create_user(user)


@router.post("/login", response_model=UserLoginResponse)
@set_auth_cookies
async def login(user: UserLoginRequest, db: DBDep, response: Response):
    return await UserService(db).login(user)


@router.post("/refresh", response_model=UserRefreshTokenResponse)
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
    refresh_token_value = refresh_token_cookie or (
        token.refresh_token if token else None
    )
    if refresh_token_value is None:
        raise InvalidTokenException()

    return await UserService(db).refresh_token(
        UserRefreshTokenRequest(refresh_token=refresh_token_value)
    )


@router.post("/logout", response_model=UserLogoutResponse)
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
    refresh_token_value = refresh_token_cookie or (
        token.refresh_token if token else None
    )
    return await UserService(db).logout(
        UserRefreshTokenRequest(refresh_token=refresh_token_value)
    )
