from fastapi import APIRouter

from app.api.schemas.user import (
    UserCreateRequest,
    UserLoginRequest,
    UserRefreshTokenRequest,
)
from app.api.dep.db import DBDep
from app.services.user import UserService

router = APIRouter()

@router.post("/")
async def create_user(user: UserCreateRequest, db: DBDep):
    return await UserService(db).create_user(user)

@router.post("/login")
async def login(user: UserLoginRequest, db: DBDep):
    return await UserService(db).login(user)


@router.post("/refresh")
async def refresh_token(token: UserRefreshTokenRequest, db: DBDep):
    return await UserService(db).refresh_token(token)