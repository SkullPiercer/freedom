from typing import Annotated

from fastapi import Depends

from app.core.db import async_session_maker
from app.db.crud import NoteCRUD, UserCRUD


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.note = NoteCRUD(self.session)
        self.user = UserCRUD(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()


async def get_db():
    async with DBManager(async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
