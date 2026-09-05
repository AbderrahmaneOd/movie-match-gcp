import json
import logging
from datetime import datetime, timezone

from app.database import get_db

logger = logging.getLogger(__name__)


class EventService:
    """Generates basic application/analytics events.

    Events are only ever best-effort and never block the application
    response. The default transport writes the event to the local event
    table (and emits a structured log line); swapping in Pub/Sub later
    keeps this interface unchanged.
    """

    def __init__(self, app):
        self.app = app

    def publish(
        self,
        event_type,
        movie_id=None,
        session_id=None,
        metadata=None,
    ):
        event = {
            "event_type": event_type,
            "movie_id": movie_id,
            "session_id": session_id,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("event event_type=%s", event_type, extra=event)
        try:
            db = get_db(self.app)
            db.execute(
                """
                INSERT INTO events (event_type, movie_id, session_id, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event_type,
                    movie_id,
                    session_id,
                    json.dumps(metadata or {}),
                ),
            )
            db.commit()
        except Exception:
            logger.exception("Failed to persist event %s", event_type)