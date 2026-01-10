import os
import json
import asyncio
import aio_pika

from app.ml.inference import predict_single
from app.schemas import PredictRequest


PREDICT_QUEUE = "predict_requests"


def _to_request(data: dict) -> PredictRequest:
    # Pydantic v1/v2 совместимость
    return PredictRequest(**data)


async def main() -> None:
    amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    connection = await aio_pika.connect_robust(amqp_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(PREDICT_QUEUE, durable=True)
    print(f"[worker] Waiting for messages in '{PREDICT_QUEUE}'...")

    async with queue.iterator() as qiterator:
        async for message in qiterator:
            async with message.process(requeue=False):
                payload = json.loads(message.body.decode("utf-8"))

                req = _to_request(payload)
                proba, label, model_version = predict_single(req)

                response = {
                    "score": float(proba),
                    "label": int(label),
                    "model_version": str(model_version),
                }

                # RPC-ответ
                if message.reply_to:
                    reply_msg = aio_pika.Message(
                        body=json.dumps(response, ensure_ascii=False).encode("utf-8"),
                        correlation_id=message.correlation_id,
                    )
                    await channel.default_exchange.publish(reply_msg, routing_key=message.reply_to)


if __name__ == "__main__":
    asyncio.run(main())
