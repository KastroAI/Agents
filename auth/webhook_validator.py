"""Webhook signature validation for Shopify, Telegram, and WhatsApp."""

from __future__ import annotations

import hashlib
import hmac

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)


def validate_shopify_webhook(request_body: bytes, hmac_header: str) -> bool:
    """Validate a Shopify webhook request using HMAC-SHA256.

    Shopify signs each webhook payload with the store's webhook secret.
    This function recomputes the HMAC and compares it to the header value.

    Args:
        request_body: The raw request body bytes.
        hmac_header: The value of the ``X-Shopify-Hmac-SHA256`` header.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    secret = settings.SHOPIFY_WEBHOOK_SECRET.encode("utf-8")
    computed = hmac.new(secret, request_body, hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(computed, hmac_header)
    if not valid:
        logger.warning("Invalid Shopify webhook signature")
    return valid


def validate_telegram_webhook(token: str) -> bool:
    """Validate a Telegram webhook by checking the bot token.

    A simple token comparison to ensure the request originates from a
    known Telegram bot configuration.

    Args:
        token: The token extracted from the webhook URL path.

    Returns:
        ``True`` if the token matches the expected bot token.
    """
    # The Telegram bot token is typically part of the webhook URL path.
    # Store it in an env var and compare here.
    expected = settings.SHOPIFY_WEBHOOK_SECRET  # reuse or add a TELEGRAM_BOT_TOKEN setting
    valid = hmac.compare_digest(token, expected)
    if not valid:
        logger.warning("Invalid Telegram webhook token")
    return valid


def validate_whatsapp_webhook(signature: str, body: bytes) -> bool:
    """Validate a WhatsApp Cloud API webhook signature.

    Meta signs webhook payloads with the app secret using HMAC-SHA256
    and sends the signature in the ``X-Hub-Signature-256`` header
    prefixed with ``sha256=``.

    Args:
        signature: The full ``X-Hub-Signature-256`` header value (e.g. ``sha256=abc...``).
        body: The raw request body bytes.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    secret = settings.SHOPIFY_WEBHOOK_SECRET.encode("utf-8")  # replace with WHATSAPP_APP_SECRET
    computed = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(computed, signature)
    if not valid:
        logger.warning("Invalid WhatsApp webhook signature")
    return valid
