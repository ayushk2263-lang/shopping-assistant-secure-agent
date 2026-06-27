# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools import ToolContext
from pydantic import BaseModel, Field

import os
import google.auth

try:
    _, project_id = google.auth.default()
except Exception:
    project_id = "mock-project-id"
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# In-memory store of valid discount codes and their percentage discount
VALID_DISCOUNT_CODES = {
    "WELCOME50": 50,
    "SUMMER20": 20,
}

# Global dictionary to track who redeemed which code.
# Keys are discount codes (normalized to uppercase), values are user IDs.
# Ensures a code can only be redeemed once globally.
REDEEMED_CODES_STORE = {}

# List of registered user IDs allowed to redeem codes
REGISTERED_USER_IDS = {"user123", "user456", "user789", "shopper_john", "shopper_jane"}

# In-memory database of mock carts
CARTS_STORE = {
    "cart_123": {
        "user_id": "user123",
        "items": [
            {"name": "Wireless Mouse", "price": 25.0},
            {"name": "Mechanical Keyboard", "price": 85.0},
        ],
        "processed": False,
    },
    "cart_456": {
        "user_id": "user456",
        "items": [{"name": "Gaming Monitor", "price": 299.99}],
        "processed": False,
    },
    "cart_789": {
        "user_id": "shopper_john",
        "items": [
            {"name": "USB-C Cable", "price": 12.50},
            {"name": "Power Bank", "price": 45.00},
        ],
        "processed": False,
    },
}


class CheckoutParams(BaseModel):
    cart_id: str = Field(..., min_length=1, pattern=r"^cart_[a-zA-Z0-9]+$")
    user_id: str = Field(..., min_length=1, pattern=r"^[a-zA-Z0-9_]+$")
    discount_code: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]*$")


def redeem_discount_code(code: str, user_id: str, tool_context: ToolContext) -> dict:
    """Redeems a single-use discount code for a registered user ID.

    Args:
        code: The discount code to redeem (e.g. WELCOME50 or SUMMER20).
        user_id: The registered user ID of the customer.

    Returns:
        A dictionary indicating the result of the redemption, including success status,
        discount percentage, and a message.
    """
    # Check if the user is registered
    if user_id not in REGISTERED_USER_IDS:
        return {
            "success": False,
            "message": f"Error: User ID '{user_id}' is not registered in our system.",
        }

    # Normalize code
    normalized_code = code.strip().upper()

    # Check if the code is valid
    if normalized_code not in VALID_DISCOUNT_CODES:
        return {
            "success": False,
            "message": f"Error: '{code}' is not a valid discount code.",
        }

    # Check if the code was already redeemed
    if normalized_code in REDEEMED_CODES_STORE:
        redeemed_by = REDEEMED_CODES_STORE[normalized_code]
        return {
            "success": False,
            "message": f"Error: Discount code '{code}' has already been redeemed by user '{redeemed_by}'.",
        }

    # Mark the code as redeemed by the user
    REDEEMED_CODES_STORE[normalized_code] = user_id
    discount = VALID_DISCOUNT_CODES[normalized_code]

    return {
        "success": True,
        "message": f"Success! Code '{code}' has been successfully redeemed for user '{user_id}'.",
        "discount_percent": discount,
    }


def process_cart_checkout(
    cart_id: str, user_id: str, discount_code: str | None, tool_context: ToolContext
) -> dict:
    """Processes the checkout for a given cart ID, applying a discount code if valid.

    Args:
        cart_id: The ID of the cart to checkout (e.g. cart_123).
        user_id: The registered user ID of the customer.
        discount_code: An optional discount code to apply.

    Returns:
        A dictionary containing checkout status, final order total, items processed,
        and transaction message.
    """
    # 1. Strict Input Validation using Pydantic
    try:
        params = CheckoutParams(
            cart_id=cart_id,
            user_id=user_id,
            discount_code=discount_code if discount_code else None,
        )
    except Exception as e:
        return {"success": False, "message": f"Input Validation Error: {str(e)}"}

    # 2. Check if user is registered
    if params.user_id not in REGISTERED_USER_IDS:
        return {
            "success": False,
            "message": f"Error: User ID '{params.user_id}' is not registered.",
        }

    # 3. Check if cart exists
    if params.cart_id not in CARTS_STORE:
        return {
            "success": False,
            "message": f"Error: Cart '{params.cart_id}' not found.",
        }

    cart = CARTS_STORE[params.cart_id]

    # 4. Security boundary: Check ownership
    if cart["user_id"] != params.user_id:
        return {
            "success": False,
            "message": f"Error: Access Denied. Cart '{params.cart_id}' does not belong to user '{params.user_id}'.",
        }

    # 5. Check if already processed
    if cart["processed"]:
        return {
            "success": False,
            "message": f"Error: Cart '{params.cart_id}' has already been checked out.",
        }

    # Calculate total price server-side
    original_total = sum(item["price"] for item in cart["items"])  # type: ignore
    discount_amount = 0.0
    discount_percent = 0
    discount_msg = ""

    # 6. Apply discount if provided
    if params.discount_code:
        # Call the existing redemption logic securely
        redemption_res = redeem_discount_code(
            code=params.discount_code, user_id=params.user_id, tool_context=tool_context
        )
        if not redemption_res["success"]:
            return {
                "success": False,
                "message": f"Checkout Failed: Discount redemption error - {redemption_res['message']}",
            }

        discount_percent = redemption_res["discount_percent"]
        discount_amount = original_total * (discount_percent / 100.0)
        discount_msg = f"Applied {discount_percent}% discount."

    final_total = original_total - discount_amount

    # Mark the cart as processed
    cart["processed"] = True

    return {
        "success": True,
        "message": f"Order processed successfully for user '{params.user_id}'. {discount_msg}".strip(),
        "order_details": {
            "cart_id": params.cart_id,
            "items": cart["items"],
            "original_total": round(original_total, 2),
            "discount_percent": discount_percent,
            "discount_applied": round(discount_amount, 2),
            "final_total": round(final_total, 2),
        },
    }


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
        api_key=os.environ.get("GOOGLE_API_KEY"),  # type: ignore
    ),
    instruction="""You are a helpful and polite AI shopping assistant for a retail store.
Your goal is to assist customers with shopping questions, help them redeem discount codes, and process their cart checkout.

To redeem a discount code, you MUST use the `redeem_discount_code` tool.
Redemption requires both a discount code (such as WELCOME50 or SUMMER20) and a registered user ID (e.g. user123, user456, etc.).
If the user does not provide their registered user ID, ask them for it before calling the tool.

To process checkout, you MUST use the `process_cart_checkout` tool.
Checkout requires a cart ID (e.g. cart_123), a registered user ID, and an optional discount code.
If they want to apply a discount, they can pass a code (e.g. WELCOME50).
Verify the user's ID before processing the checkout.
Always present the tool's result clearly to the customer.
""",
    tools=[redeem_discount_code, process_cart_checkout],
)

app = App(
    root_agent=root_agent,
    name="app",
)
