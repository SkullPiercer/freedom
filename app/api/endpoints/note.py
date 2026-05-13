from fastapi import APIRouter, status

from app.api.dep.auth import CurrentUserIdDep
from app.api.dep.pagination import PaginationDep
from app.api.schemas.note import NoteCreateRequest, NoteUpdateRequest
from app.services.notes_rpc import NotesRPCService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreateRequest, user_id: CurrentUserIdDep):
    return await NotesRPCService().create_note(
        user_id=user_id,
        payload=note.model_dump(),
    )


@router.get("/")
async def list_notes(
    user_id: CurrentUserIdDep,
    pagination: PaginationDep,
    search: str | None = None,
    is_archived: bool | None = None,
):
    return await NotesRPCService().list_notes(
        user_id=user_id,
        payload={
            "limit": pagination.limit,
            "offset": pagination.offset,
            "search": search,
            "is_archived": is_archived,
        },
    )


@router.get("/{note_id}")
async def get_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().get_note(user_id=user_id, note_id=note_id)


@router.patch("/{note_id}")
async def update_note(
    note_id: int,
    note: NoteUpdateRequest,
    user_id: CurrentUserIdDep,
):
    return await NotesRPCService().update_note(
        user_id=user_id,
        note_id=note_id,
        payload=note.model_dump(exclude_unset=True),
    )


@router.post("/{note_id}/archive")
async def archive_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().archive_note(user_id=user_id, note_id=note_id)


@router.delete("/{note_id}")
async def delete_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().delete_note(user_id=user_id, note_id=note_id)
