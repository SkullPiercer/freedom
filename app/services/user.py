from asyncpg.exceptions import UniqueViolationError

from app.api.schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserCreateSchema,
    UserDBSchema,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserPublicSchema,
    UserRefreshTokenRequest,
    UserRefreshTokenResponse,
)
from app.exceptions.auth import InvalidTokenException
from app.exceptions.base import DataAlreadyExistsException
from app.exceptions.user import InvalidPasswordException, UserNotFoundException
from app.services.base import BaseService
from app.services.password import PasswordService
from app.services.token import TokenService


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

    def create_user_public_schema(self, user) -> UserPublicSchema:
        return UserPublicSchema(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def create_auth_response(self, user, response_schema):
        tokens = await self.token_service.create_token_pair(user.id)
        return response_schema(
            user=self.create_user_public_schema(user),
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
