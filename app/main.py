import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from app.core.config import settings
from app.core.db import check_db_connection

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(_: FastAPI):
    await check_db_connection()
    logger.info("Соединение с базой данных установлено")
    yield

app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)