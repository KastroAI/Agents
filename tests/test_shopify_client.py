"""Tests for ShopifyClient using httpx mocking."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from shared.shopify_client import ShopifyClient


@pytest.fixture()
def shopify() -> ShopifyClient:
    """Return a ShopifyClient with mocked settings."""
    with patch("shared.shopify_client.settings") as mock_settings:
        mock_settings.SHOPIFY_STORE_URL = "https://jaded-rose.myshopify.com"
        mock_settings.SHOPIFY_ADMIN_API_KEY = "test-key"
        client = ShopifyClient()
        yield client


class TestGetOrder:
    """Tests for ShopifyClient.get_order()."""

    def test_returns_order_dict(self, shopify: ShopifyClient) -> None:
        """get_order should return the order as a plain dict."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "order": {"id": 123, "name": "#JR-0001", "total_price": "49.99"}
        }
        mock_response.raise_for_status = MagicMock()

        shopify._client.get = MagicMock(return_value=mock_response)
        result = shopify.get_order(123)

        assert result["id"] == 123
        assert result["name"] == "#JR-0001"
        assert result["total_price"] == "49.99"


class TestGetOrderByName:
    """Tests for ShopifyClient.get_order_by_name()."""

    def test_returns_matching_order(self, shopify: ShopifyClient) -> None:
        """Should return the first matching order dict."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "orders": [{"id": 456, "name": "#JR-4821"}]
        }
        mock_response.raise_for_status = MagicMock()

        shopify._client.get = MagicMock(return_value=mock_response)
        result = shopify.get_order_by_name("#JR-4821")

        assert result is not None
        assert result["name"] == "#JR-4821"

    def test_returns_none_when_not_found(self, shopify: ShopifyClient) -> None:
        """Should return None when no order matches the name."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"orders": []}
        mock_response.raise_for_status = MagicMock()

        shopify._client.get = MagicMock(return_value=mock_response)
        result = shopify.get_order_by_name("#NONEXISTENT")

        assert result is None


class TestGetProducts:
    """Tests for ShopifyClient.get_products()."""

    def test_returns_product_list(self, shopify: ShopifyClient) -> None:
        """Should return a list of product dicts."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "products": [
                {"id": 1, "title": "Silk Blouse"},
                {"id": 2, "title": "Linen Trousers"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        shopify._client.get = MagicMock(return_value=mock_response)
        result = shopify.get_products(limit=10)

        assert len(result) == 2
        assert result[0]["title"] == "Silk Blouse"


class TestGetFulfillment:
    """Tests for ShopifyClient.get_fulfillment()."""

    def test_returns_fulfillment_list(self, shopify: ShopifyClient) -> None:
        """Should return a list of fulfillment dicts for an order."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "fulfillments": [
                {"id": 789, "status": "success", "tracking_number": "TRACK123"}
            ]
        }
        mock_response.raise_for_status = MagicMock()

        shopify._client.get = MagicMock(return_value=mock_response)
        result = shopify.get_fulfillment(123)

        assert len(result) == 1
        assert result[0]["tracking_number"] == "TRACK123"
