from unittest.mock import MagicMock

import pytest
from google.adk.tools import ToolContext

from app.agent import (
    REDEEMED_CODES_STORE,
    redeem_discount_code,
)


@pytest.fixture(autouse=True)
def clean_redeemed_store():
    # Clear the redeemed codes store before each test to ensure test isolation
    REDEEMED_CODES_STORE.clear()


def test_redeem_discount_code_success() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Successful redemption for registered user and valid code
    result = redeem_discount_code(
        code="WELCOME50", user_id="user123", tool_context=mock_context
    )

    assert result["success"] is True
    assert result["discount_percent"] == 50
    assert "successfully redeemed" in result["message"]
    assert REDEEMED_CODES_STORE["WELCOME50"] == "user123"


def test_redeem_discount_code_unregistered_user() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Try to redeem with an unregistered user ID
    result = redeem_discount_code(
        code="WELCOME50", user_id="anonymous_user", tool_context=mock_context
    )

    assert result["success"] is False
    assert "is not registered in our system" in result["message"]
    assert "WELCOME50" not in REDEEMED_CODES_STORE


def test_redeem_discount_code_invalid_code() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Try to redeem an invalid code
    result = redeem_discount_code(
        code="FAKECODE100", user_id="user123", tool_context=mock_context
    )

    assert result["success"] is False
    assert "is not a valid discount code" in result["message"]
    assert "FAKECODE100" not in REDEEMED_CODES_STORE


def test_redeem_discount_code_single_use_restriction() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Redeem WELCOME50 first time
    first_res = redeem_discount_code(
        code="WELCOME50", user_id="user123", tool_context=mock_context
    )
    assert first_res["success"] is True

    # Try to redeem WELCOME50 a second time
    second_res = redeem_discount_code(
        code="WELCOME50", user_id="user456", tool_context=mock_context
    )

    assert second_res["success"] is False
    assert "already been redeemed" in second_res["message"]
    assert (
        REDEEMED_CODES_STORE["WELCOME50"] == "user123"
    )  # Still owned by first redeemer


def test_redeem_discount_code_normalization() -> None:
    mock_context = MagicMock(spec=ToolContext)

    # Test that whitespace is trimmed and casing is normalized
    result = redeem_discount_code(
        code="   summer20   ", user_id="user123", tool_context=mock_context
    )

    assert result["success"] is True
    assert result["discount_percent"] == 20
    assert REDEEMED_CODES_STORE["SUMMER20"] == "user123"
