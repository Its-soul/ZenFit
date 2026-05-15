from uuid import UUID

from redis import Redis
from sqlalchemy.orm import Session

from app.core.redis_client import get_redis_client
from app.events.event_bus import RedisEventBus
from app.events.models import DomainEvent


class EventProducer:
    def __init__(self, db: Session, redis_client: Redis | None = None):
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.event_bus = RedisEventBus(self.redis)

    def emit(self, *, user_id: UUID, event_type: str, payload: dict) -> DomainEvent:
        event = DomainEvent(user_id=user_id, event_type=event_type, payload=payload)
        self.db.add(event)
        self.db.flush()

        self.event_bus.publish_event(event_id=event.id, user_id=user_id, event_type=event_type)
        return event
