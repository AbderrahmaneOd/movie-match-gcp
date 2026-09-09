from datetime import datetime, timezone
import json
import logging

from app.extensions import db

from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)


class EventService:
    """Best-effort analytics event writer.

    Events are persisted to the ``events`` table and never block the
    application response.  In a future GCP deployment the writer can be
    swapped to Pub/Sub without changing the public interface.
    """
    def __init__(self, gcp_project_id, topic_id):
        self.gcp_project_id = gcp_project_id
        self.topic_id = topic_id

        # Avoid initializing Pub/Sub client locally if running offline
        if self.gcp_project_id:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(self.gcp_project_id, self.topic_id)
        else:
            self.publisher = None
        
    # def publish(
    #     self,
    #     event_type,
    #     movie_id=None,
    #     session_id=None,
    #     metadata=None,
    # ):
    #     try:
    #         db.session.add(
    #             Event(
    #                 event_type=event_type,
    #                 movie_id=movie_id,
    #                 session_id=session_id,
    #                 metadata_json=json.dumps(metadata or {}),
    #             )
    #         )
    #         db.session.commit()
    #         logger.info("event event_type=%s", event_type)
    #     except Exception:
    #         db.session.rollback()
    #         logger.exception("Failed to persist event %s", event_type)
            
    
    def publish_to_pubsub(self, event_type, movie_id=None, session_id=None, metadata=None):
        
        event_payload = {
            "event_type": event_type,
            "session_id": session_id,
            "movie_id": movie_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        # Local development graceful fallback
        if not self.publisher:
            print(f"[LOCAL EVENT]: {event_payload}")
            return

        try:
            # Pub/Sub payload must be byte-encoded JSON
            data = json.dumps(event_payload).encode("utf-8")
            future = self.publisher.publish(self.topic_path, data)
            future.result(timeout=5)  # Wait for confirmation
        except Exception as e:
            # Handle analytics logging failures gracefully without breaking the user request
            logger.exception("Failed to publish event to Pub/Sub")