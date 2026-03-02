"""Tests for comms.telegram helpers."""

from __future__ import annotations

from comms.telegram import _normalize_message_update


def test_normalize_message_update() -> None:
    raw = {
        "update_id": 1,
        "message": {
            "message_id": 10,
            "date": 1700000000,
            "text": "hello",
            "chat": {"id": 42, "type": "private"},
            "from": {"id": 99, "is_bot": False, "first_name": "Test"},
        },
    }
    result = _normalize_message_update(raw)

    assert result is not None
    assert result["text"] == "hello"
    assert result["chat"]["id"] == 42
    assert result["sender"]["id"] == 99
    assert result["message_type"] == "message"


def test_normalize_returns_none_for_non_message() -> None:
    assert _normalize_message_update({"update_id": 1}) is None


def test_normalize_edited_message() -> None:
    raw = {
        "update_id": 2,
        "edited_message": {
            "message_id": 11,
            "date": 1700000001,
            "text": "edited",
            "chat": {"id": 42, "type": "private"},
            "from": {"id": 99, "is_bot": False},
        },
    }
    result = _normalize_message_update(raw)

    assert result is not None
    assert result["message_type"] == "edited_message"
    assert result["text"] == "edited"
