import os
import json
import asyncio
import uuid
from typing import Any, Dict, Optional

import aio_pika


PREDICT_QUEUE = "predict_requests"


class RpcClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractChannel] = None
        self.callback_queue: Optional[aio_pika.abc.AbstractQueue] = None
        self._futures: Dict[str, asyncio.Future] = {}

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        # Очередь запросов (на всякий случай объявим и тут)
        await self.channel.declare_queue(PREDICT_QUEUE, durable=True)

        # Callback очередь (эксклюзивная, авто-удаляемая)
        self.callback_queue = await self.channel.declare_queue(exclusive=True)

        await self.callback_queue.consume(self._on_response, no_ack=True)

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def _on_response(self, message: aio_pika.IncomingMessage) -> None:
        corr_id = message.correlation_id
        if not corr_id:
            return
        fut = self._futures.pop(corr_id, None)
        if fut and not fut.done():
            fut.set_result(message.body)

    async def predict(self, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        if not self.channel or not self.callback_queue:
            raise RuntimeError("RPC client is not connected")

        corr_id = str(uuid.uuid4())
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._futures[corr_id] = fut

        message = aio_pika.Message(
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            correlation_id=corr_id,
            reply_to=self.callback_queue.name,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.channel.default_exchange.publish(message, routing_key=PREDICT_QUEUE)

        raw = await asyncio.wait_for(fut, timeout=timeout)
        return json.loads(raw.decode("utf-8"))


def get_amqp_url() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
