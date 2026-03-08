"""OpenAI API client with exponential backoff on rate-limit errors."""

from __future__ import annotations

from typing import Any

import openai
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Wrapper around the OpenAI Python SDK for chat completions and embeddings."""

    def __init__(self) -> None:
        """Initialise the OpenAI client with the configured API key."""
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(openai.RateLimitError),
        reraise=True,
    )
    def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.2,
    ) -> str:
        """Send a chat completion request and return the assistant reply.

        Args:
            messages: Conversation history as a list of role/content dicts.
            system_prompt: Optional system message prepended to the conversation.
            model: The OpenAI model to use.
            temperature: Sampling temperature.

        Returns:
            The assistant's reply text.
        """
        full_messages: list[dict[str, str]] = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        logger.info("OpenAI chat request", extra={"model": model})
        response = self._client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        return content

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(openai.RateLimitError),
        reraise=True,
    )
    def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        logger.info("OpenAI embed request")
        response = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(openai.RateLimitError),
        reraise=True,
    )
    def chat_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        system_prompt: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.2,
    ) -> Any:
        """Send a chat completion request with tool definitions.

        Args:
            messages: Conversation history.
            tools: List of tool/function definitions in OpenAI format.
            system_prompt: Optional system message.
            model: The OpenAI model to use.
            temperature: Sampling temperature.

        Returns:
            The full ChatCompletion response object so callers can inspect
            tool calls and decide how to proceed.
        """
        full_messages: list[dict[str, str]] = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        logger.info("OpenAI chat_with_tools request", extra={"model": model, "tool_count": len(tools)})
        response = self._client.chat.completions.create(
            model=model,
            messages=full_messages,
            tools=tools,
            temperature=temperature,
        )
        return response
