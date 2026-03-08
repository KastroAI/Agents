"""Pinecone vector database client with retry logic."""

from __future__ import annotations

from typing import Any

from pinecone import Pinecone, ServerlessSpec
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)


class PineconeClient:
    """Wrapper around the Pinecone SDK for vector upsert, query, and delete operations."""

    def __init__(self) -> None:
        """Initialise the Pinecone client using application settings."""
        self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self._index_name = settings.PINECONE_INDEX_NAME
        self._index = self.get_or_create_index()

    def get_or_create_index(self) -> Any:
        """Return the Pinecone index, creating it if it does not already exist.

        Returns:
            The Pinecone index object.
        """
        existing = [idx.name for idx in self._pc.list_indexes()]
        if self._index_name not in existing:
            logger.info(
                "Creating Pinecone index",
                extra={"index_name": self._index_name},
            )
            self._pc.create_index(
                name=self._index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="gcp", region=settings.PINECONE_ENVIRONMENT),
            )
        return self._pc.Index(self._index_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def upsert(self, vectors: list[tuple[str, list[float], dict[str, Any]]], namespace: str) -> dict[str, Any]:
        """Upsert vectors into the specified namespace.

        Args:
            vectors: List of (id, embedding, metadata) tuples.
            namespace: The Pinecone namespace to write to.

        Returns:
            The upsert response from Pinecone.
        """
        logger.info(
            "Upserting vectors",
            extra={"namespace": namespace, "count": len(vectors)},
        )
        response = self._index.upsert(vectors=vectors, namespace=namespace)
        return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def query(
        self,
        embedding: list[float],
        namespace: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Query the index for similar vectors.

        Args:
            embedding: The query vector.
            namespace: The Pinecone namespace to search.
            top_k: Number of results to return.

        Returns:
            The query response containing matches.
        """
        logger.info(
            "Querying vectors",
            extra={"namespace": namespace, "top_k": top_k},
        )
        response = self._index.query(
            vector=embedding,
            namespace=namespace,
            top_k=top_k,
            include_metadata=True,
        )
        return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def delete(self, ids: list[str], namespace: str) -> dict[str, Any]:
        """Delete vectors by their IDs from a namespace.

        Args:
            ids: List of vector IDs to delete.
            namespace: The Pinecone namespace to delete from.

        Returns:
            The delete response from Pinecone.
        """
        logger.info(
            "Deleting vectors",
            extra={"namespace": namespace, "count": len(ids)},
        )
        response = self._index.delete(ids=ids, namespace=namespace)
        return response
