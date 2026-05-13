from app.services.base import BaseService
from app.api.schemas.user import UserCreateRequest, UserCreateSchema

class UserService(BaseService):
    async def create_user(self, user: UserCreateRequest):
        password = user.password.get_secret_value()
        validated_data = UserCreateSchema(
            email=user.email, hashed_password=password
        )
        new_user = await self.db.user.create(validated_data)

        await self.db.commit()
        return new_user