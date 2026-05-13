from fastapi import APIRouter

from app.api.schemas.user import UserCreate

router = APIRouter()

@router.post("/")
async def create_user(user: UserCreate):
    return {"message": "User created", "user": user}
