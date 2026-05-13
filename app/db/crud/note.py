from datetime import datetime

from sqlalchemy import delete, func, or_, select, update

from app.api.schemas.note import NoteCreateRequest, NoteCreateSchema, NoteUpdateRequest
from app.db.crud.base import CRUDBase
from app.db.crud.mappers.note import NoteDataMapper
from app.db.models.note import Note


class NoteCRUD(CRUDBase):
    model = Note
    mapper = NoteDataMapper

    async def create_for_user(self, user_id: int, note: NoteCreateRequest):
        return await self.create(
            NoteCreateSchema(
                title=note.title,
                content=note.content,
                user_id=user_id,
            )
        )

    async def list_for_user(
        self,
        user_id: int,
        limit: int,
        offset: int,
        search: str | None = None,
        is_archived: bool | None = None,
    ):
        filters = [self.model.user_id == user_id]

        if is_archived is not None:
            filters.append(self.model.is_archived == is_archived)

        if search:
            search_expr = f"%{search}%"
            filters.append(
                or_(
                    self.model.title.ilike(search_expr),
                    self.model.content.ilike(search_expr),
                )
            )

        total_query = select(func.count()).select_from(self.model).where(*filters)
        total = await self.session.scalar(total_query)

        query = (
            select(self.model)
            .where(*filters)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        notes = result.scalars().all()

        return {
            "items": [self.mapper.map_to_domain_entity(note) for note in notes],
            "total": total or 0,
        }

    async def get_for_user(self, user_id: int, note_id: int):
        query = select(self.model).where(
            self.model.id == note_id,
            self.model.user_id == user_id,
        )
        result = await self.session.execute(query)
        note = result.scalars().one_or_none()
        if note is None:
            return None
        return self.mapper.map_to_domain_entity(note)

    async def update_for_user(
        self,
        user_id: int,
        note_id: int,
        note: NoteUpdateRequest,
    ):
        values = note.model_dump(exclude_unset=True)
        if not values:
            return await self.get_for_user(user_id=user_id, note_id=note_id)

        query = (
            update(self.model)
            .where(self.model.id == note_id, self.model.user_id == user_id)
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        updated_note = result.scalars().one_or_none()
        if updated_note is None:
            return None
        return self.mapper.map_to_domain_entity(updated_note)

    async def archive_for_user(self, user_id: int, note_id: int):
        query = (
            update(self.model)
            .where(self.model.id == note_id, self.model.user_id == user_id)
            .values(is_archived=True, archived_at=datetime.utcnow())
            .returning(self.model)
        )
        result = await self.session.execute(query)
        archived_note = result.scalars().one_or_none()
        if archived_note is None:
            return None
        return self.mapper.map_to_domain_entity(archived_note)

    async def delete_for_user(self, user_id: int, note_id: int) -> bool:
        query = delete(self.model).where(
            self.model.id == note_id,
            self.model.user_id == user_id,
        )
        result = await self.session.execute(query)
        return result.rowcount > 0
