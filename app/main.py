import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from app.core.config import settings
from app.core.db import check_db_connection, engine
from app.api.routers import main_router
from app.exceptions import register_exception_handlers
from app.connectors.redis_connector import redis_manager

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(_: FastAPI):
    await redis_manager.connect()
    logger.info("Redis connected successfully")

    await check_db_connection()
    logger.info("Database connected")
    yield

    await redis_manager.disconnect()
    logger.info("Redis disconnected")

    await engine.dispose()
    logger.info("Database disconnected")

app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.include_router(main_router)
register_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)