import json
import logging
import time
from dataclasses import dataclass
from uuid import UUID

from redis import Redis

from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

EVENT_QUEUE = "fitness.events.queue"
EVENT_RETRY_QUEUE = "fitness.events.retry"
REALTIME_CHANNEL = "fitness.realtime"


@dataclass
class EventMessage:
    event_id: str
    user_id: str
    event_type: str
    attempts: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_id": self.event_id,
                "user_id": self.user_id,
                "event_type": self.event_type,
                "attempts": self.attempts,
            }
        )

    @classmethod
    def from_json(cls, raw_message: str) -> "EventMessage":
        payload = json.loads(raw_message)
        return cls(
            event_id=payload["event_id"],
            user_id=payload["user_id"],
            event_type=payload["event_type"],
            attempts=payload.get("attempts", 0),
        )


class RedisEventBus:
    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or get_redis_client()

    def publish_event(self, *, event_id: UUID, user_id: UUID, event_type: str) -> None:
        message = EventMessage(event_id=str(event_id), user_id=str(user_id), event_type=event_type)
        self.redis.lpush(EVENT_QUEUE, message.to_json())
        self.redis.publish("fitness.events", message.to_json())

    def consume_event(self, timeout_seconds: int = 5) -> EventMessage | None:
        result = self.redis.brpop(EVENT_QUEUE, timeout=timeout_seconds)
        if not result:
            return None
        _, raw_message = result
        return EventMessage.from_json(raw_message)

    def retry_event(self, message: EventMessage, max_attempts: int = 3) -> None:
        message.attempts += 1
        if message.attempts > max_attempts:
            logger.exception("Event exceeded retry limit: %s", message)
            self.redis.lpush(EVENT_RETRY_QUEUE, message.to_json())
            return

        time.sleep(min(2 * message.attempts, 10))
        self.redis.lpush(EVENT_QUEUE, message.to_json())

    def publish_realtime(self, *, user_id: str, event_type: str, payload: dict) -> None:
        self.redis.publish(
            REALTIME_CHANNEL,
            json.dumps({"user_id": user_id, "type": event_type, "payload": payload}),
        )

