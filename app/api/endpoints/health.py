from fastapi import APIRouter

from app.api.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return {"status": "ok"}
