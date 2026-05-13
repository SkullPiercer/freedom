from functools import cached_property, lru_cache
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class PostgresSettings(BaseModel):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DB: str

    @cached_property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.DB}"
        )   


class RedisSettings(BaseModel):
    HOST: str
    PORT: int
    PASSWORD: str

    @cached_property
    def REDIS_URL(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}"


class JWTSettings(BaseModel):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int


class CookieSettings(BaseModel):
    SECURE: bool = False
    SAMESITE: Literal["lax", "strict", "none"] = "lax"


class Settings(BaseSettings):
    APP_TITLE: str
    MODE: Literal['local', 'dev', 'prod', 'test'] = 'local'

    POSTGRES: PostgresSettings
    REDIS: RedisSettings

    JWT: JWTSettings
    COOKIE: CookieSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()