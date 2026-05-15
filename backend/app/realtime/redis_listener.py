import asyncio
import json
import logging

from redis.asyncio import Redis

from app.config import settings
from app.events.event_bus import REALTIME_CHANNEL
from app.realtime.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


async def listen_for_realtime_messages(stop_event: asyncio.Event) -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(REALTIME_CHANNEL)
    logger.info("Realtime Redis listener subscribed to %s", REALTIME_CHANNEL)

    try:
        while not stop_event.is_set():
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if not message:
                continue

            try:
                payload = json.loads(message["data"])
                await websocket_manager.send_to_user(
                    payload["user_id"],
                    {"type": payload["type"], "payload": payload.get("payload", {})},
                )
            except Exception:
                logger.exception("Failed to forward realtime Redis message")
    finally:
        await pubsub.unsubscribe(REALTIME_CHANNEL)
        await pubsub.close()
        await redis.close()

