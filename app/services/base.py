from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.dep.db import DBManager


class BaseService:
    db: "DBManager | None"

    def __init__(self, db: "DBManager | None" = None):
        self.db = db