from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr, field_validator


class UserEmailSchema(BaseModel):
    email: EmailStr


class UserPasswordSchema(BaseModel):
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserCreateRequest(UserEmailSchema, UserPasswordSchema):
    pass


class UserCreateSchema(UserEmailSchema):
    hashed_password: str


class UserDBSchema(UserCreateSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TokenPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class AuthTokenResponse(TokenPairSchema):
    pass


class UserAuthResponse(AuthTokenResponse):
    user: UserDBSchema


class UserCreateResponse(UserAuthResponse):
    pass


class UserLoginRequest(UserEmailSchema, UserPasswordSchema):
    pass


class UserLoginResponse(UserAuthResponse):
    pass


class UserRefreshTokenRequest(BaseModel):
    refresh_token: str | None = None


class UserRefreshTokenResponse(AuthTokenResponse):
    pass


class UserLogoutResponse(BaseModel):
    message: str
