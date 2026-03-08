"""GCP Pub/Sub task queue for inter-agent communication."""

from __future__ import annotations

import json
from typing import Any, Callable

from google.cloud import pubsub_v1

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)


class TaskQueue:
    """Publish and subscribe to GCP Pub/Sub topics."""

    def __init__(self) -> None:
        """Initialise the Pub/Sub publisher and subscriber clients."""
        self._publisher = pubsub_v1.PublisherClient()
        self._subscriber = pubsub_v1.SubscriberClient()
        self._project_id = settings.GCP_PROJECT_ID

    def publish(self, topic: str, message: dict[str, Any]) -> str:
        """Publish a JSON-serialised message to a Pub/Sub topic.

        Args:
            topic: The short topic name (not the full resource path).
            message: The message payload to serialise and publish.

        Returns:
            The Pub/Sub message ID as a string.
        """
        topic_path = self._publisher.topic_path(self._project_id, topic)
        data = json.dumps(message).encode("utf-8")

        logger.info("Publishing message", extra={"topic": topic})
        future = self._publisher.publish(topic_path, data=data)
        message_id = future.result()
        logger.info("Message published", extra={"topic": topic, "message_id": message_id})
        return message_id

    def subscribe(self, subscription: str, callback: Callable[[dict[str, Any]], None]) -> None:
        """Start a blocking subscription that delivers messages to *callback*.

        Each incoming message is deserialised from JSON and acknowledged
        automatically after the callback completes without error.

        Args:
            subscription: The short subscription name.
            callback: A callable that receives the deserialised message dict.
        """
        subscription_path = self._subscriber.subscription_path(
            self._project_id, subscription
        )

        def _wrapped(message: pubsub_v1.subscriber.message.Message) -> None:
            """Deserialise and forward the message, then ack."""
            try:
                data: dict[str, Any] = json.loads(message.data.decode("utf-8"))
                logger.info(
                    "Received message",
                    extra={"subscription": subscription, "message_id": message.message_id},
                )
                callback(data)
                message.ack()
            except Exception:
                logger.exception(
                    "Error processing message",
                    extra={"subscription": subscription, "message_id": message.message_id},
                )
                message.nack()

        logger.info("Starting subscription", extra={"subscription": subscription})
        streaming_pull_future = self._subscriber.subscribe(subscription_path, callback=_wrapped)

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result()
            logger.info("Subscription cancelled", extra={"subscription": subscription})
