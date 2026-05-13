from fastapi import HTTPException, status

from app.connectors.rabbitmq_connector import rabbitmq_manager
from app.core.config import settings


class NotesRPCService:
    async def call(self, action: str, user_id: int, payload: dict | None = None):
        response = await rabbitmq_manager.call(
            queue_name=settings.RABBITMQ.NOTES_QUEUE,
            payload={
                "action": action,
                "user_id": user_id,
                "payload": payload or {},
            },
        )

        if not response.get("ok"):
            raise HTTPException(
                status_code=response.get(
                    "status_code",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                detail=response.get("error", "Notes worker error"),
            )

        return response.get("data")

    async def create_note(self, user_id: int, payload: dict):
        return await self.call("create_note", user_id=user_id, payload=payload)

    async def list_notes(self, user_id: int, payload: dict):
        return await self.call("list_notes", user_id=user_id, payload=payload)

    async def get_note(self, user_id: int, note_id: int):
        return await self.call("get_note", user_id=user_id, payload={"note_id": note_id})

    async def update_note(self, user_id: int, note_id: int, payload: dict):
        return await self.call(
            "update_note",
            user_id=user_id,
            payload={"note_id": note_id, **payload},
        )

    async def archive_note(self, user_id: int, note_id: int):
        return await self.call(
            "archive_note",
            user_id=user_id,
            payload={"note_id": note_id},
        )

    async def delete_note(self, user_id: int, note_id: int):
        return await self.call(
            "delete_note",
            user_id=user_id,
            payload={"note_id": note_id},
        )
