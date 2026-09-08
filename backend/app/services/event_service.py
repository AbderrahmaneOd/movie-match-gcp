import json
import logging

from app.extensions import db
from app.models.favorite import Event

logger = logging.getLogger(__name__)


class EventService:
    """Best-effort analytics event writer.

    Events are persisted to the ``events`` table and never block the
    application response.  In a future GCP deployment the writer can be
    swapped to Pub/Sub without changing the public interface.
    """

    def publish(
        self,
        event_type,
        movie_id=None,
        session_id=None,
        metadata=None,
    ):
        try:
            db.session.add(
                Event(
                    event_type=event_type,
                    movie_id=movie_id,
                    session_id=session_id,
                    metadata_json=json.dumps(metadata or {}),
                )
            )
            db.session.commit()
            logger.info("event event_type=%s", event_type)
        except Exception:
            db.session.rollback()
            logger.exception("Failed to persist event %s", event_type)