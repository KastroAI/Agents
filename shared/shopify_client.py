"""Shopify Admin API client returning clean Python dicts."""

from __future__ import annotations

from typing import Any

import httpx

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)

_API_VERSION = "2024-01"


class ShopifyClient:
    """HTTP client for the Shopify Admin REST API.

    All methods return plain Python dicts rather than raw Shopify objects.
    """

    def __init__(self) -> None:
        """Initialise the Shopify client with store URL and credentials."""
        base = settings.SHOPIFY_STORE_URL.rstrip("/")
        self._base_url = f"{base}/admin/api/{_API_VERSION}"
        self._headers = {
            "X-Shopify-Access-Token": settings.SHOPIFY_ADMIN_API_KEY,
            "Content-Type": "application/json",
        }
        self._client = httpx.Client(headers=self._headers, timeout=30.0)

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def get_order(self, order_id: int) -> dict[str, Any]:
        """Fetch a single order by its Shopify ID.

        Args:
            order_id: The numeric Shopify order ID.

        Returns:
            A dict representing the order.
        """
        url = f"{self._base_url}/orders/{order_id}.json"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()["order"]

    def get_order_by_name(self, order_name: str) -> dict[str, Any] | None:
        """Find an order by its human-readable name (e.g. '#JR-4821').

        Args:
            order_name: The order name including the '#' prefix.

        Returns:
            The matching order dict, or None if not found.
        """
        url = f"{self._base_url}/orders.json"
        params = {"name": order_name, "status": "any", "limit": 1}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        orders = response.json().get("orders", [])
        return orders[0] if orders else None

    def get_orders(self, limit: int = 50, status: str = "any") -> list[dict[str, Any]]:
        """Fetch a list of orders.

        Args:
            limit: Maximum number of orders to return.
            status: Order status filter ('open', 'closed', 'cancelled', 'any').

        Returns:
            A list of order dicts.
        """
        url = f"{self._base_url}/orders.json"
        params = {"limit": limit, "status": status}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("orders", [])

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    def get_products(self, limit: int = 250) -> list[dict[str, Any]]:
        """Fetch a list of products.

        Args:
            limit: Maximum number of products to return.

        Returns:
            A list of product dicts.
        """
        url = f"{self._base_url}/products.json"
        params = {"limit": limit}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("products", [])

    def get_product(self, product_id: int) -> dict[str, Any]:
        """Fetch a single product by its Shopify ID.

        Args:
            product_id: The numeric Shopify product ID.

        Returns:
            A dict representing the product.
        """
        url = f"{self._base_url}/products/{product_id}.json"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()["product"]

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def get_inventory_levels(self) -> list[dict[str, Any]]:
        """Fetch inventory levels for all locations.

        Returns:
            A list of inventory level dicts.
        """
        # First get the locations
        locations_url = f"{self._base_url}/locations.json"
        loc_response = self._client.get(locations_url)
        loc_response.raise_for_status()
        locations = loc_response.json().get("locations", [])

        all_levels: list[dict[str, Any]] = []
        for location in locations:
            url = f"{self._base_url}/inventory_levels.json"
            params = {"location_ids": location["id"], "limit": 250}
            response = self._client.get(url, params=params)
            response.raise_for_status()
            all_levels.extend(response.json().get("inventory_levels", []))
        return all_levels

    def update_inventory(self, inventory_item_id: int, location_id: int, quantity: int) -> dict[str, Any]:
        """Set the available quantity for an inventory item at a location.

        Args:
            inventory_item_id: The inventory item ID.
            location_id: The location ID.
            quantity: The new available quantity.

        Returns:
            The updated inventory level dict.
        """
        url = f"{self._base_url}/inventory_levels/set.json"
        payload = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": quantity,
        }
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("inventory_level", {})

    # ------------------------------------------------------------------
    # Fulfillments
    # ------------------------------------------------------------------

    def get_fulfillment(self, order_id: int) -> list[dict[str, Any]]:
        """Fetch fulfillments for a given order.

        Args:
            order_id: The numeric Shopify order ID.

        Returns:
            A list of fulfillment dicts.
        """
        url = f"{self._base_url}/orders/{order_id}/fulfillments.json"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json().get("fulfillments", [])
