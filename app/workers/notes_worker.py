import asyncio
import json
import logging

import aio_pika
from fastapi import status

from app.api.dep.db import DBManager
from app.api.schemas.note import NoteCreateRequest, NoteListResponse, NoteUpdateRequest
from app.core.config import settings
from app.core.db import async_session_maker, engine

logger = logging.getLogger(__name__)


def dump_model(model):
    return model.model_dump(mode="json")


async def handle_notes_request(message: dict) -> dict:
    action = message.get("action")
    user_id = message.get("user_id")
    payload = message.get("payload") or {}

    if user_id is None:
        return {
            "ok": False,
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "error": "User is required",
        }

    async with DBManager(async_session_maker) as db:
        if action == "create_note":
            note = await db.note.create_for_user(
                user_id=user_id,
                note=NoteCreateRequest(**payload),
            )
            await db.commit()
            return {"ok": True, "data": dump_model(note)}

        if action == "list_notes":
            limit = payload.get("limit", 20)
            offset = payload.get("offset", 0)
            result = await db.note.list_for_user(
                user_id=user_id,
                limit=limit,
                offset=offset,
                search=payload.get("search"),
                is_archived=payload.get("is_archived"),
            )
            response = NoteListResponse(
                items=result["items"],
                limit=limit,
                offset=offset,
                total=result["total"],
            )
            return {"ok": True, "data": dump_model(response)}

        if action == "get_note":
            note = await db.note.get_for_user(
                user_id=user_id,
                note_id=payload["note_id"],
            )
            if note is None:
                return {
                    "ok": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Note not found",
                }
            return {"ok": True, "data": dump_model(note)}

        if action == "update_note":
            note_id = payload.pop("note_id")
            note = await db.note.update_for_user(
                user_id=user_id,
                note_id=note_id,
                note=NoteUpdateRequest(**payload),
            )
            if note is None:
                return {
                    "ok": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Note not found",
                }
            await db.commit()
            return {"ok": True, "data": dump_model(note)}

        if action == "archive_note":
            note = await db.note.archive_for_user(
                user_id=user_id,
                note_id=payload["note_id"],
            )
            if note is None:
                return {
                    "ok": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Note not found",
                }
            await db.commit()
            return {"ok": True, "data": dump_model(note)}

        if action == "delete_note":
            is_deleted = await db.note.delete_for_user(
                user_id=user_id,
                note_id=payload["note_id"],
            )
            if not is_deleted:
                return {
                    "ok": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "error": "Note not found",
                }
            await db.commit()
            return {"ok": True, "data": {"message": "Note deleted successfully"}}

    return {
        "ok": False,
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error": f"Unknown action: {action}",
    }


async def main():
    connection = await aio_pika.connect_robust(settings.RABBITMQ.URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(settings.RABBITMQ.NOTES_QUEUE, durable=True)

    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                request = json.loads(message.body.decode())
                response = await handle_notes_request(request)
            except Exception as exc:
                logger.exception("Failed to process notes request")
                response = {
                    "ok": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(exc),
                }

            if message.reply_to:
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response).encode(),
                        content_type="application/json",
                        correlation_id=message.correlation_id,
                    ),
                    routing_key=message.reply_to,
                )

    await queue.consume(on_message)
    logger.info("Notes worker started")

    try:
        await asyncio.Future()
    finally:
        await connection.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
