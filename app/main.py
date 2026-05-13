import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.routers import main_router
from app.connectors.rabbitmq_connector import rabbitmq_manager
from app.connectors.redis_connector import redis_manager
from app.core.config import settings
from app.core.db import check_db_connection, engine
from app.exceptions import register_exception_handlers

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await redis_manager.connect()
    await rabbitmq_manager.connect()
    await check_db_connection()
    yield

    await rabbitmq_manager.disconnect()
    logger.info("RabbitMQ disconnected")

    await redis_manager.disconnect()
    logger.info("Redis disconnected")

    await engine.dispose()
    logger.info("Database disconnected")


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.include_router(main_router)
register_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
