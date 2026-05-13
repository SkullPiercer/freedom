from app.db.crud.mappers.base import DataMapper
from app.db.models.user import User
from app.api.schemas.user import UserDBSchema

class UserDataMapper(DataMapper):
    model = User
    schema = UserDBSchema