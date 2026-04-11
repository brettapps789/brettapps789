"""
utils/stripe_api.py

Helper class for Stripe API operations used by @Manager.

Covers:
  - Customer creation / retrieval
  - Subscription creation
  - Invoice retrieval

The STRIPE_API_KEY environment variable must be set before instantiation.
"""

import logging
import os
from typing import Any

import stripe

logger = logging.getLogger(__name__)


class StripeHelper:
    """
    Thin wrapper around the Stripe Python SDK.

    All methods are synchronous and intended to be run via
    ``asyncio.to_thread`` in the async agents.
    """

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("STRIPE_API_KEY")
        if not key:
            raise ValueError(
                "Stripe API key must be provided via the STRIPE_API_KEY "
                "environment variable or the api_key constructor argument."
            )
        stripe.api_key = key

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def get_or_create_customer(self, email: str) -> dict[str, Any]:
        """
        Return the first existing Stripe customer with *email*, or create one.
        """
        existing = stripe.Customer.list(email=email, limit=1)
        if existing.data:
            customer = existing.data[0]
            logger.info("[Stripe] Found existing customer %s", customer["id"])
            return dict(customer)

        customer = stripe.Customer.create(email=email)
        logger.info("[Stripe] Created new customer %s", customer["id"])
        return dict(customer)

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(self, email: str, plan_id: str) -> dict[str, Any]:
        """
        Create a Stripe subscription for the customer identified by *email*
        using *plan_id* (a Stripe Price ID such as ``price_xxx``).

        If the customer already has an active subscription to this plan the
        existing subscription is returned instead.
        """
        customer = self.get_or_create_customer(email)
        customer_id = customer["id"]

        active_subs = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=10,
        )
        for sub in active_subs.data:
            for item in sub["items"]["data"]:
                if item["price"]["id"] == plan_id:
                    logger.info(
                        "[Stripe] Customer %s already subscribed to %s", customer_id, plan_id
                    )
                    return dict(sub)

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": plan_id}],
        )
        logger.info("[Stripe] Created subscription %s", subscription["id"])
        return dict(subscription)

    def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel a subscription immediately."""
        sub = stripe.Subscription.cancel(subscription_id)
        logger.info("[Stripe] Cancelled subscription %s", subscription_id)
        return dict(sub)

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    def get_latest_invoice(self, customer_email: str) -> dict[str, Any] | None:
        """Return the latest invoice for the customer with *customer_email*."""
        customer = self.get_or_create_customer(customer_email)
        invoices = stripe.Invoice.list(customer=customer["id"], limit=1)
        if invoices.data:
            return dict(invoices.data[0])
        return None
