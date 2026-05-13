from app.api.schemas.note import NoteDBSchema
from app.db.crud.mappers.base import DataMapper
from app.db.models.note import Note


class NoteDataMapper(DataMapper):
    model = Note
    schema = NoteDBSchema
