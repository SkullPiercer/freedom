from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr, field_validator

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserCreateSchema(BaseModel):
    email: EmailStr
    hashed_password: str


class UserDBSchema(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class TokenPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserCreateResponse(BaseModel):
    user: UserDBSchema
    access_token: str
    refresh_token: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class UserLoginResponse(BaseModel):
    user: UserDBSchema
    access_token: str
    refresh_token: str


class UserRefreshTokenRequest(BaseModel):
    refresh_token: str


class UserRefreshTokenResponse(BaseModel):
    access_token: str