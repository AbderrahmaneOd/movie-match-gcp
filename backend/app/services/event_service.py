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
    
    def publish_to_pubsub(self, event_type, movie_id=None, session_id=None, metadata=None):
        
        event_payload = {
            "event_type": event_type,
            "session_id": session_id,
            "movie_id": movie_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata":  json.dumps(metadata or {})
        }

        # Local development graceful fallback
        if not self.publisher:
            logger.info( "LOCAL EVENT: event_type=%s payload=%s", event_type, event_payload)
            return

        try:
            # Pub/Sub payload must be byte-encoded JSON
            data = json.dumps(event_payload).encode("utf-8")
            logger.info( "Publishing event to Pub/Sub: topic=%s event_type=%s payload=%s", self.topic_path, event_type, event_payload)
            future = self.publisher.publish(self.topic_path, data)
            message_id = future.result(timeout=5)  # Wait for confirmation
            logger.info( "Event published successfully: event_type=%s message_id=%s", event_type, message_id)
        except Exception as e:
            logger.exception( "Failed to publish event to Pub/Sub: " "event_type=%s payload=%s", event_type, event_payload)