from sqlalchemy import select

from app.db.crud.base import CRUDBase
from app.db.crud.mappers.user import UserDataMapper
from app.db.models.user import User

class UserCRUD(CRUDBase):
    model = User
    mapper = UserDataMapper

    async def get_by_email(self, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return self.mapper.map_to_domain_entity(result.scalars().one_or_none())
