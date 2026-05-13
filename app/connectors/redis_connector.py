import logging

import redis.asyncio as redis

from app.core.config import get_settings


class RedisConnector:
    def __init__(self, url, port, password):
        self.url = url
        self.port = port
        self.password = password
        self.redis = None

    async def connect(self):
        logging.info(f"Trying to connect to Redis: {self.url}:{self.port}")
        self.redis = redis.Redis(
            host=self.url,
            port=self.port,
            password=self.password,
            decode_responses=True,
        )
        await self.redis.ping()
        logging.info("Redis connected successfully")

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, exp: int = None):
        if exp:
            await self.redis.set(key, value, ex=exp)
        else:
            await self.redis.set(key, value)

    async def incr_with_expire(self, key: str, exp: int) -> int:
        value = await self.redis.incr(key)
        if value == 1:
            await self.redis.expire(key, exp)
        return int(value)

    async def delete(self, key: str):
        await self.redis.delete(key)


settings = get_settings()
redis_manager = RedisConnector(
    settings.REDIS.HOST,
    settings.REDIS.PORT,
    settings.REDIS.PASSWORD,
)
