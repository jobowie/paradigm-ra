import os

from decimal import Decimal, ROUND_HALF_UP

import stripe

from ra_platform.billing.models import (
    Invoice,
    Quote,
)


class StripeConfigurationError(
    RuntimeError
):
    pass


def get_stripe_secret_key() -> str:
    key = os.getenv(
        "STRIPE_SECRET_KEY"
    )

    if not key:
        raise StripeConfigurationError(
            "STRIPE_SECRET_KEY "
            "is not configured."
        )

    return key


def get_stripe_webhook_secret() -> str:
    secret = os.getenv(
        "STRIPE_WEBHOOK_SECRET"
    )

    if not secret:
        raise StripeConfigurationError(
            "STRIPE_WEBHOOK_SECRET "
            "is not configured."
        )

    return secret


def dollars_to_cents(
    amount: Decimal,
) -> int:
    normalized = amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return int(
        normalized * 100
    )


def create_deposit_checkout_session(
    *,
    quote: Quote,
    invoice: Invoice,
    success_url: str,
    cancel_url: str,
):
    stripe.api_key = (
        get_stripe_secret_key()
    )

    metadata = {
        "quote_id": str(
            quote.id
        ),
        "quote_number": (
            quote.quote_number
        ),
        "invoice_id": str(
            invoice.id
        ),
        "invoice_number": (
            invoice.invoice_number
        ),
        "payment_type": (
            "project_deposit"
        ),
    }

    kwargs = {
        "mode": "payment",
        "client_reference_id": str(
            quote.id
        ),
        "line_items": [
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": (
                            f"{quote.quote_number} "
                            "— Project Deposit"
                        ),
                        "description": (
                            quote.bill_to_name
                        ),
                    },
                    "unit_amount": (
                        dollars_to_cents(
                            invoice.total
                        )
                    ),
                },
                "quantity": 1,
            }
        ],
        "metadata": metadata,
        "payment_intent_data": {
            "metadata": metadata,
        },
        "success_url": success_url,
        "cancel_url": cancel_url,
    }

    if quote.bill_to_email:
        kwargs["customer_email"] = (
            quote.bill_to_email
        )

    return stripe.checkout.Session.create(
        **kwargs,
        idempotency_key=(
            f"deposit-checkout-"
            f"{invoice.id}"
        ),
    )


def construct_webhook_event(
    *,
    payload: bytes,
    signature: str,
):
    return stripe.Webhook.construct_event(
        payload,
        signature,
        get_stripe_webhook_secret(),
    )
