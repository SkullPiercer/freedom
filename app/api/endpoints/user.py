from fastapi import APIRouter

from app.api.schemas.user import UserCreateRequest
from app.api.dep.db import DBDep
from app.services.user import UserService

router = APIRouter()

@router.post("/")
async def create_user(user: UserCreateRequest, db: DBDep):
    return await UserService(db).create_user(user)
