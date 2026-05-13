from app.db.crud.base import CRUDBase
from app.db.crud.mappers.user import UserDataMapper
from app.db.models.user import User

class UserCRUD(CRUDBase):
    model = User
    mapper = UserDataMapper
