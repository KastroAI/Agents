"""Routes tasks to the correct agent via GCP Pub/Sub."""

from __future__ import annotations

from typing import Any

from config.constants import (
    CHATBOT_AGENT,
    DATA_AGENT,
    INTELLIGENCE_AGENT,
    OUTREACH_AGENT,
    ORDER_TRACKING,
    FAQ,
    PRODUCT_QUERY,
    RETURNS,
    ESCALATE,
)
from config.settings import settings
from orchestrator.task_queue import TaskQueue
from shared.logger import get_logger

logger = get_logger(__name__)

# Maps task types to the agent responsible for handling them.
_TASK_AGENT_MAP: dict[str, str] = {
    ORDER_TRACKING: CHATBOT_AGENT,
    FAQ: CHATBOT_AGENT,
    PRODUCT_QUERY: CHATBOT_AGENT,
    RETURNS: CHATBOT_AGENT,
    ESCALATE: CHATBOT_AGENT,
    "product_sync": DATA_AGENT,
    "inventory_sync": DATA_AGENT,
    "weekly_report": INTELLIGENCE_AGENT,
    "trend_analysis": INTELLIGENCE_AGENT,
    "competitor_scrape": INTELLIGENCE_AGENT,
    "email_outreach": OUTREACH_AGENT,
    "follow_up": OUTREACH_AGENT,
}


class AgentRouter:
    """Determines the correct agent for a task and publishes it to Pub/Sub."""

    def __init__(self) -> None:
        """Initialise the router with a TaskQueue instance."""
        self._queue = TaskQueue()
        self._topic = settings.GCP_PUBSUB_TOPIC

    def route(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Route a task to the appropriate agent.

        Looks up the agent for *task_type*, enriches the payload, and publishes
        the message to the configured Pub/Sub topic.

        Args:
            task_type: A string identifying the kind of task (e.g. ``'order_tracking'``).
            payload: Arbitrary data associated with the task.

        Returns:
            A dict containing ``agent``, ``task_type``, and ``message_id``.

        Raises:
            ValueError: If *task_type* is not recognised.
        """
        agent = _TASK_AGENT_MAP.get(task_type)
        if agent is None:
            logger.error("Unknown task type", extra={"task_type": task_type})
            raise ValueError(f"Unknown task type: {task_type}")

        message = {
            "agent": agent,
            "task_type": task_type,
            "payload": payload,
        }

        logger.info(
            "Routing task",
            extra={"task_type": task_type, "agent": agent},
        )

        message_id = self._queue.publish(self._topic, message)

        return {
            "agent": agent,
            "task_type": task_type,
            "message_id": message_id,
        }
