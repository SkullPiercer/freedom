import logging

import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from app.services.base import BaseService
from app.api.schemas.user import UserCreateRequest, UserCreateResponse, UserCreateSchema
from app.core.config import settings

class PasswordService:
    password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.password_hash.hash(password)


class TokenService:
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode["exp"] = expire
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT.SECRET_KEY, algorithm=settings.JWT.ALGORITHM
        )
        return encoded_jwt

    def decode_access_token(self, data: str) -> dict:
        try:
            return jwt.decode(
                data, settings.JWT.SECRET_KEY, algorithms=[settings.JWT.ALGORITHM]
            )
        except Exception as e:
            logging.error(e)
            raise Exception(f"Failed to decode token: {e}")
    

class UserService(BaseService):
    password_service = PasswordService()
    token_service = TokenService()

    async def create_user(self, user: UserCreateRequest) -> UserCreateResponse:
        password = user.password.get_secret_value()
        validated_data = UserCreateSchema(
            email=user.email,
            hashed_password=self.password_service.get_password_hash(password)
        )
        new_user = await self.db.user.create(validated_data)
        access_token = self.token_service.create_access_token({"user_id": new_user.id})

        await self.db.commit()
        return UserCreateResponse(
            user=new_user,
            access_token=access_token,
        )