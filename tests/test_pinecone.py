"""Tests for agent_tools.pinecone helpers."""

from __future__ import annotations

from agent_tools.pinecone import EmbeddingModel


def test_embedding_model_values() -> None:
    assert EmbeddingModel.SMALL.value == "text-embedding-3-small"
    assert EmbeddingModel.LARGE.value == "text-embedding-3-large"


def test_embedding_model_from_string() -> None:
    assert EmbeddingModel("text-embedding-3-small") is EmbeddingModel.SMALL
    assert EmbeddingModel("text-embedding-3-large") is EmbeddingModel.LARGE
