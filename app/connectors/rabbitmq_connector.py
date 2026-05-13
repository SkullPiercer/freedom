import asyncio
import json
from uuid import uuid4

import aio_pika
import logging
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from app.core.config import settings

logging = logging.getLogger("uvicorn.error")

class RabbitMQConnector:
    def __init__(self, url: str):
        self.url = url
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.callback_queue: aio_pika.Queue | None = None
        self.futures: dict[str, asyncio.Future] = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        logging.info("RabbitMQ connected successfully")

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def on_response(self, message: aio_pika.IncomingMessage):
        correlation_id = message.correlation_id
        if correlation_id is None:
            return

        future = self.futures.pop(correlation_id, None)
        if future is not None:
            future.set_result(json.loads(message.body.decode()))

    async def call(self, queue_name: str, payload: dict, timeout: int = 10) -> dict:
        if self.channel is None or self.callback_queue is None:
            raise RuntimeError("RabbitMQ connector is not connected")

        correlation_id = str(uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[correlation_id] = future

        await self.channel.declare_queue(queue_name, durable=True)
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=queue_name,
        )

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self.futures.pop(correlation_id, None)


rabbitmq_manager = RabbitMQConnector(settings.RABBITMQ.URL)
