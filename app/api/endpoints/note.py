from typing import Annotated

from fastapi import APIRouter, Body, status

from app.api.dep.auth import CurrentUserIdDep
from app.api.dep.pagination import PaginationDep
from app.api.examples.note import note_examples
from app.api.schemas.note import (
    NoteCreateRequest,
    NoteDBSchema,
    NoteDeleteResponse,
    NoteListResponse,
    NoteUpdateRequest,
)
from app.services.notes_rpc import NotesRPCService

router = APIRouter()


@router.post("/", response_model=NoteDBSchema, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: Annotated[NoteCreateRequest, Body(..., openapi_examples=note_examples)],
    user_id: CurrentUserIdDep,
):
    return await NotesRPCService().create_note(
        user_id=user_id,
        payload=note.model_dump(),
    )


@router.get("/", response_model=NoteListResponse)
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


@router.get("/{note_id}", response_model=NoteDBSchema)
async def get_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().get_note(user_id=user_id, note_id=note_id)


@router.patch("/{note_id}", response_model=NoteDBSchema)
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


@router.post("/{note_id}/archive", response_model=NoteDBSchema)
async def archive_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().archive_note(user_id=user_id, note_id=note_id)


@router.delete("/{note_id}", response_model=NoteDeleteResponse)
async def delete_note(note_id: int, user_id: CurrentUserIdDep):
    return await NotesRPCService().delete_note(user_id=user_id, note_id=note_id)
