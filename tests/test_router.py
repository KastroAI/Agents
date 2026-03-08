"""Tests for the AgentRouter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

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
from orchestrator.agent_router import AgentRouter


@pytest.fixture()
def router() -> AgentRouter:
    """Return an AgentRouter with a mocked TaskQueue."""
    with patch("orchestrator.agent_router.TaskQueue") as mock_queue_cls:
        mock_queue = MagicMock()
        mock_queue.publish.return_value = "msg-123"
        mock_queue_cls.return_value = mock_queue
        r = AgentRouter()
        yield r


class TestAgentRouter:
    """Test suite for AgentRouter.route()."""

    @pytest.mark.parametrize(
        "task_type,expected_agent",
        [
            (ORDER_TRACKING, CHATBOT_AGENT),
            (FAQ, CHATBOT_AGENT),
            (PRODUCT_QUERY, CHATBOT_AGENT),
            (RETURNS, CHATBOT_AGENT),
            (ESCALATE, CHATBOT_AGENT),
            ("product_sync", DATA_AGENT),
            ("inventory_sync", DATA_AGENT),
            ("weekly_report", INTELLIGENCE_AGENT),
            ("trend_analysis", INTELLIGENCE_AGENT),
            ("competitor_scrape", INTELLIGENCE_AGENT),
            ("email_outreach", OUTREACH_AGENT),
            ("follow_up", OUTREACH_AGENT),
        ],
    )
    def test_routes_to_correct_agent(
        self, router: AgentRouter, task_type: str, expected_agent: str
    ) -> None:
        """Each task type should be dispatched to the correct agent."""
        result = router.route(task_type, {"key": "value"})
        assert result["agent"] == expected_agent
        assert result["task_type"] == task_type
        assert result["message_id"] == "msg-123"

    def test_unknown_task_type_raises(self, router: AgentRouter) -> None:
        """An unrecognised task type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown task type"):
            router.route("nonexistent_task", {})

    def test_publish_called_with_correct_message(self, router: AgentRouter) -> None:
        """The router should publish the enriched message to the queue."""
        router.route(ORDER_TRACKING, {"order_id": 42})
        router._queue.publish.assert_called_once()
        call_args = router._queue.publish.call_args
        message = call_args[0][1]
        assert message["agent"] == CHATBOT_AGENT
        assert message["task_type"] == ORDER_TRACKING
        assert message["payload"] == {"order_id": 42}
