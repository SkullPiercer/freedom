from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class Pagination(BaseModel):
    page: Annotated[int, Query(1, ge=1, description="Номер страницы")]
    per_page: Annotated[int, Query(20, ge=1, le=100, description="Заметок на странице")]

    @property
    def limit(self) -> int:
        return self.per_page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


PaginationDep = Annotated[Pagination, Depends()]
