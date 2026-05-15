import logging
import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.events.event_bus import EventMessage, RedisEventBus
from app.events.handlers.ai_event_handler import AIEventHandler
from app.events.models import DomainEvent

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(self, db: Session):
        self.db = db
        self.bus = RedisEventBus()
        self.handler = AIEventHandler(db)

    def run_forever(self) -> None:
        logger.info("AI event worker started")
        while True:
            message = self.bus.consume_event(timeout_seconds=5)
            if message is None:
                continue
            self.process_message(message)

    def process_message(self, message: EventMessage) -> None:
        try:
            event = self._load_event(message)
            if event is None:
                # The API may have queued before its DB transaction committed.
                self.bus.retry_event(message)
                return

            if event.processed:
                return

            logger.info("Processing event %s (%s)", event.id, event.event_type)
            self.handler.handle(event)
        except Exception:
            logger.exception("Failed to process event message: %s", message)
            self.db.rollback()
            self.bus.retry_event(message)

    def _load_event(self, message: EventMessage) -> DomainEvent | None:
        try:
            event_id = UUID(message.event_id)
        except ValueError:
            logger.warning("Invalid event id in message: %s", message.event_id)
            return None

        for _ in range(4):
            event = self.db.scalar(select(DomainEvent).where(DomainEvent.id == event_id))
            if event:
                return event
            time.sleep(0.5)
        return None

