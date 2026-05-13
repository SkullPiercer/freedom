from pydantic import BaseModel, EmailStr, SecretStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value