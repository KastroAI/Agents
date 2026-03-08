"""Structured JSON logging with agent-aware fields."""

from __future__ import annotations

import logging
import sys
import uuid

from pythonjsonlogger import jsonlogger


_DEFAULT_FORMAT = "%(timestamp)s %(level)s %(name)s %(message)s"

# Module-level trace ID; overridden per-request in production.
_trace_id: str = uuid.uuid4().hex[:12]


class _JadedRoseFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that injects standard fields."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        """Add timestamp, level, agent_name and trace_id to every log entry."""
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["agent_name"] = getattr(record, "agent_name", record.name)
        log_record["trace_id"] = getattr(record, "trace_id", _trace_id)


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured for structured JSON output.

    Args:
        name: The logger name, typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = _JadedRoseFormatter(_DEFAULT_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger
