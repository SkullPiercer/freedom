from datetime import datetime

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class NoteCreateRequest(NoteBase):
    pass


class NoteUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)


class NoteCreateSchema(NoteBase):
    user_id: int


class NoteDBSchema(NoteCreateSchema):
    id: int
    is_archived: bool
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteDBSchema]
    limit: int
    offset: int
    total: int


class NoteDeleteResponse(BaseModel):
    message: str
