import logging

from app.db.session import SessionLocal
from app.core.qdrant_client import ensure_qdrant_collections
from app.events.consumer import EventConsumer
from app.ai.registry import registry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def main() -> None:
    ensure_qdrant_collections()
    registry.prewarm()
    db = SessionLocal()
    try:
        EventConsumer(db).run_forever()
    finally:
        db.close()


if __name__ == "__main__":
    main()
