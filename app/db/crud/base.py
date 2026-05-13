from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.mappers.base import DataMapper

class CRUDBase:
    model = None
    mapper: DataMapper = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj):
        query = (
            insert(self.model).values(**obj.model_dump()).returning(self.model)
        )
        result = await self.session.execute(query)
        return self.mapper.map_to_domain_entity(result.scalars().one())