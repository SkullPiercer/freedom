from fastapi import APIRouter

from app.api.endpoints import health_router, note_router, user_router

main_router = APIRouter()

main_router.include_router(health_router, prefix="/health", tags=["health"])
main_router.include_router(note_router, prefix="/notes", tags=["notes"])
main_router.include_router(user_router, prefix="/auth", tags=["auth"])
