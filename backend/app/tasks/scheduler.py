import logging
import time

from app.core.qdrant_client import ensure_qdrant_collections
from app.tasks.scheduled_jobs import run_once

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def main() -> None:
    ensure_qdrant_collections()
    while True:
        try:
            run_once()
        except Exception:
            logging.exception("Scheduled AI jobs failed")
        time.sleep(60 * 60 * 6)


if __name__ == "__main__":
    main()

