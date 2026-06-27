from unittest.mock import MagicMock

import pytest
from google.adk.tools import ToolContext

from app.agent import (
    CARTS_STORE,
    REDEEMED_CODES_STORE,
    process_cart_checkout,
)


@pytest.fixture(autouse=True)
def reset_stores():
    # Reset stores before each test to ensure isolation
    CARTS_STORE["cart_123"]["processed"] = False
    CARTS_STORE["cart_456"]["processed"] = False
    CARTS_STORE["cart_789"]["processed"] = False
    REDEEMED_CODES_STORE.clear()


def test_tool_process_cart_checkout_success() -> None:
    # Set up mock tool context
    mock_context = MagicMock(spec=ToolContext)

    # Process cart_123 for user123 without discount
    result = process_cart_checkout(
        cart_id="cart_123",
        user_id="user123",
        discount_code=None,
        tool_context=mock_context,
    )

    assert result["success"] is True
    assert result["order_details"]["original_total"] == 110.0
    assert result["order_details"]["final_total"] == 110.0
    assert result["order_details"]["discount_percent"] == 0
    assert CARTS_STORE["cart_123"]["processed"] is True


def test_tool_process_cart_checkout_unauthorized() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Try to process cart_123 (belongs to user123) under user456
    result = process_cart_checkout(
        cart_id="cart_123",
        user_id="user456",
        discount_code=None,
        tool_context=mock_context,
    )

    assert result["success"] is False
    assert "Access Denied" in result["message"]
    assert CARTS_STORE["cart_123"]["processed"] is False


def test_tool_process_cart_checkout_already_processed() -> None:
    mock_context = MagicMock(spec=ToolContext)
    CARTS_STORE["cart_123"]["processed"] = True

    result = process_cart_checkout(
        cart_id="cart_123",
        user_id="user123",
        discount_code=None,
        tool_context=mock_context,
    )

    assert result["success"] is False
    assert "already been checked out" in result["message"]


def test_tool_process_cart_checkout_pydantic_validation() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Invalid cart_id (does not start with cart_)
    result = process_cart_checkout(
        cart_id="invalid_id",
        user_id="user123",
        discount_code=None,
        tool_context=mock_context,
    )

    assert result["success"] is False
    assert "Input Validation Error" in result["message"]


def test_tool_process_cart_checkout_with_discount() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Process cart_123 for user123 with SUMMER20 (20%)
    result = process_cart_checkout(
        cart_id="cart_123",
        user_id="user123",
        discount_code="SUMMER20",
        tool_context=mock_context,
    )

    assert result["success"] is True
    assert result["order_details"]["original_total"] == 110.0
    assert result["order_details"]["discount_percent"] == 20
    assert result["order_details"]["discount_applied"] == 22.0
    assert result["order_details"]["final_total"] == 88.0
    assert REDEEMED_CODES_STORE["SUMMER20"] == "user123"


def test_tool_process_cart_checkout_discount_already_redeemed() -> None:
    mock_context = MagicMock(spec=ToolContext)
    REDEEMED_CODES_STORE["SUMMER20"] = "user456"

    # Try to redeem SUMMER20 again
    result = process_cart_checkout(
        cart_id="cart_123",
        user_id="user123",
        discount_code="SUMMER20",
        tool_context=mock_context,
    )

    assert result["success"] is False
    assert "already been redeemed" in result["message"]
    assert CARTS_STORE["cart_123"]["processed"] is False
