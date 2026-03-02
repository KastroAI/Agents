"""Tests for agent_tools.simple_memory.Memory."""

from __future__ import annotations

import json
from pathlib import Path

from agent_tools.simple_memory import Memory


def test_save_and_load(tmp_path: Path) -> None:
    path = tmp_path / "mem.json"
    mem = Memory(path=path, max_entries=5)
    entry = mem.save("user", "hello")

    assert entry["role"] == "user"
    assert entry["content"] == "hello"
    assert "timestamp" in entry

    loaded = Memory(path=path, max_entries=5)
    assert len(loaded.history) == 1
    assert loaded.history[0]["content"] == "hello"


def test_max_entries_cap(tmp_path: Path) -> None:
    path = tmp_path / "mem.json"
    mem = Memory(path=path, max_entries=3)

    for i in range(5):
        mem.save("user", f"msg-{i}")

    assert len(mem.history) == 3
    assert mem.history[0]["content"] == "msg-2"
    assert mem.history[-1]["content"] == "msg-4"


def test_clear(tmp_path: Path) -> None:
    path = tmp_path / "mem.json"
    mem = Memory(path=path)
    mem.save("user", "keep")
    mem.clear()

    assert mem.history == []
    assert json.loads(path.read_text()) == []


def test_history_returns_copy(tmp_path: Path) -> None:
    path = tmp_path / "mem.json"
    mem = Memory(path=path)
    mem.save("user", "hi")

    history = mem.history
    history.clear()
    assert len(mem.history) == 1
