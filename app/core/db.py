import logging
from datetime import datetime

from sqlalchemy import DateTime, Integer, func, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class PreBase:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


engine = create_async_engine(settings.POSTGRES.DB_URL)

Base = declarative_base(cls=PreBase)

async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def check_db_connection():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT version()"))
        logger.info("Database version: %s", res.fetchone())
