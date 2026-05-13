from app.api.schemas.user import UserDBSchema
from app.db.crud.mappers.base import DataMapper
from app.db.models.user import User


class UserDataMapper(DataMapper):
    model = User
    schema = UserDBSchema
