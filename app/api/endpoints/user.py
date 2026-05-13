from fastapi import APIRouter, Response

from app.api.schemas.user import (
    UserCreateRequest,
    UserLoginRequest,
    UserRefreshTokenRequest,
)
from app.api.dep.db import DBDep
from app.services.user import UserService
from app.api.api_decorators.user import set_auth_cookies

router = APIRouter()

@router.post("/")
async def create_user(user: UserCreateRequest, db: DBDep):
    return await UserService(db).create_user(user)


@router.post("/login")
@set_auth_cookies
async def login(user: UserLoginRequest, db: DBDep, response: Response):
    return await UserService(db).login(user)


@router.post("/refresh")
@set_auth_cookies
async def refresh_token(token: UserRefreshTokenRequest, db: DBDep, response: Response):
    return await UserService(db).refresh_token(token)