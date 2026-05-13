import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from asyncpg.exceptions import UniqueViolationError
from jwt import PyJWTError
from pwdlib import PasswordHash

from app.api.schemas.user import (
    TokenPairSchema,
    UserCreateRequest,
    UserCreateResponse,
    UserCreateSchema,
    UserDBSchema,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserRefreshTokenRequest,
    UserRefreshTokenResponse,
)
from app.connectors.redis_connector import redis_manager
from app.core.config import settings
from app.exceptions.auth import InvalidTokenException
from app.exceptions.base import DataAlreadyExistsException
from app.exceptions.user import InvalidPasswordException, UserNotFoundException
from app.services.base import BaseService


class PasswordService:
    password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.password_hash.hash(password)


class TokenService:
    refresh_token_key_prefix = "refresh_token"

    def get_refresh_token_key(self, jti: str) -> str:
        return f"{self.refresh_token_key_prefix}:{jti}"

    def create_token(
        self, data: dict, expires_delta: timedelta, token_type: str
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode["exp"] = expire
        to_encode["type"] = token_type
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT.SECRET_KEY, algorithm=settings.JWT.ALGORITHM
        )
        return encoded_jwt

    def create_access_token(self, data: dict) -> str:
        return self.create_token(
            data=data,
            expires_delta=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access",
        )

    def create_refresh_token(self, data: dict, jti: str) -> str:
        return self.create_token(
            data={**data, "jti": jti},
            expires_delta=timedelta(minutes=settings.JWT.REFRESH_TOKEN_EXPIRE_MINUTES),
            token_type="refresh",
        )

    async def save_refresh_token(self, user_id: int, jti: str) -> None:
        await redis_manager.set(
            key=self.get_refresh_token_key(jti),
            value=str(user_id),
            exp=settings.JWT.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def create_token_pair(self, user_id: int) -> TokenPairSchema:
        jti = str(uuid4())
        token_data = {"user_id": user_id}
        await self.save_refresh_token(user_id=user_id, jti=jti)
        return TokenPairSchema(
            access_token=self.create_access_token(token_data),
            refresh_token=self.create_refresh_token(token_data, jti=jti),
        )

    def decode_token(self, data: str, token_type: str) -> dict:
        try:
            payload = jwt.decode(
                data, settings.JWT.SECRET_KEY, algorithms=[settings.JWT.ALGORITHM]
            )
            if payload.get("type") != token_type:
                raise InvalidTokenException()
            return payload
        except PyJWTError as e:
            logging.error(e)
            raise InvalidTokenException() from e

    def decode_access_token(self, data: str) -> dict:
        return self.decode_token(data, token_type="access")

    def decode_refresh_token(self, data: str) -> dict:
        return self.decode_token(data, token_type="refresh")

    async def validate_refresh_token(self, refresh_token: str) -> dict:
        payload = self.decode_refresh_token(refresh_token)
        user_id = payload.get("user_id")
        jti = payload.get("jti")

        if user_id is None or jti is None:
            raise InvalidTokenException()

        stored_user_id = await redis_manager.get(self.get_refresh_token_key(jti))
        if stored_user_id != str(user_id):
            raise InvalidTokenException()

        return payload

    async def rotate_refresh_token(self, refresh_token: str) -> TokenPairSchema:
        payload = await self.validate_refresh_token(refresh_token)
        user_id = payload["user_id"]
        jti = payload["jti"]

        await redis_manager.delete(self.get_refresh_token_key(jti))
        return await self.create_token_pair(user_id=user_id)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        payload = await self.validate_refresh_token(refresh_token)
        await redis_manager.delete(self.get_refresh_token_key(payload["jti"]))


class UserService(BaseService):
    password_service = PasswordService()
    token_service = TokenService()

    def create_user_db_schema(self, user) -> UserDBSchema:
        return UserDBSchema(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def create_auth_response(self, user, response_schema):
        tokens = await self.token_service.create_token_pair(user.id)
        return response_schema(
            user=self.create_user_db_schema(user),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def create_user(self, user: UserCreateRequest) -> UserCreateResponse:
        password = user.password.get_secret_value()
        validated_data = UserCreateSchema(
            email=user.email,
            hashed_password=self.password_service.get_password_hash(password),
        )
        try:
            new_user = await self.db.user.create(validated_data)

            await self.db.commit()

        except Exception as e:
            orig = getattr(e, "orig", None)
            if isinstance(getattr(orig, "__cause__", None), UniqueViolationError):
                raise DataAlreadyExistsException()
            raise

        return await self.create_auth_response(new_user, UserCreateResponse)

    async def login(self, user: UserLoginRequest) -> UserLoginResponse:
        db_user = await self.db.user.get_by_email(user.email)
        if not db_user:
            raise UserNotFoundException()
        if not self.password_service.verify_password(
            user.password.get_secret_value(),
            db_user.hashed_password,
        ):
            raise InvalidPasswordException()
        return await self.create_auth_response(db_user, UserLoginResponse)

    async def refresh_token(
        self,
        token: UserRefreshTokenRequest,
    ) -> UserRefreshTokenResponse:
        if not token.refresh_token:
            raise InvalidTokenException()

        tokens = await self.token_service.rotate_refresh_token(token.refresh_token)
        return UserRefreshTokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def logout(self, token: UserRefreshTokenRequest) -> UserLogoutResponse:
        if token.refresh_token:
            await self.token_service.revoke_refresh_token(token.refresh_token)

        return UserLogoutResponse(message="Logged out successfully")
