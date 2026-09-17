import os
import sqlite3

from datetime import (
    date,
    datetime,
    timezone,
)
from decimal import Decimal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from pydantic import BaseModel

from ra_platform.api.dependencies import (
    get_database_connection,
    get_database_path,
)
from ra_platform.billing.models import (
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    QuoteStatus,
)
from ra_platform.billing.service import (
    create_invoice_from_accepted_quote,
    refresh_invoice,
)
from ra_platform.payments.persistence import (
    SQLitePaymentPersistence,
)
from ra_platform.payments.stripe import (
    StripeConfigurationError,
    construct_webhook_event,
    create_deposit_checkout_session,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteQuoteRepository,
)
from ra_platform.security.tokens import (
    hash_public_token,
)


router = APIRouter(
    tags=["payments"],
)


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    invoice_number: str
    amount: str


class DepositStatusResponse(BaseModel):
    deposit_amount: str
    invoice_number: str | None
    invoice_status: str | None
    amount_paid: str
    balance_due: str
    deposit_paid: bool


def get_deposit_line(quote):
    return next(
        (
            line
            for line in quote.line_items
            if "deposit"
            in line.description.lower()
        ),
        None,
    )


def next_invoice_number(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT COUNT(*) AS invoice_count
        FROM invoices
        """
    ).fetchone()

    count = int(
        row["invoice_count"]
    ) + 1

    return (
        f"RA-INV-"
        f"{date.today().year}-"
        f"{count:03d}"
    )


def ensure_deposit_invoice(
    *,
    quote,
    connection: sqlite3.Connection,
    persistence: SQLitePaymentPersistence,
):
    existing = (
        persistence
        .get_deposit_invoice_for_quote(
            quote.id
        )
    )

    if existing is not None:
        return existing

    deposit = get_deposit_line(
        quote
    )

    if deposit is None:
        raise ValueError(
            "Quote does not contain "
            "a project deposit."
        )

    existing_invoices = (
        persistence
        .get_invoices_for_quote(
            quote.id
        )
    )

    invoice = (
        create_invoice_from_accepted_quote(
            quote=quote,
            invoice_number=(
                next_invoice_number(
                    connection
                )
            ),
            invoice_amount=deposit.amount,
            description=deposit.description,
            issue_date=date.today(),
            due_date=date.today(),
            existing_invoices=(
                existing_invoices
            ),
        )
    )

    invoice.status = (
        InvoiceStatus.SENT
    )

    persistence.invoices.add(
        invoice
    )

    return invoice


@router.post(
    "/quotes/public/{token}/checkout",
    response_model=CheckoutResponse,
)
def create_quote_checkout(
    token: str,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteQuoteRepository(
        connection
    )

    quote = (
        repository
        .get_by_public_token_hash(
            hash_public_token(token)
        )
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found.",
        )

    if (
        quote.status
        != QuoteStatus.ACCEPTED
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Quote must be accepted "
                "before payment."
            ),
        )

    persistence = (
        SQLitePaymentPersistence(
            connection
        )
    )

    try:
        invoice = (
            ensure_deposit_invoice(
                quote=quote,
                connection=connection,
                persistence=persistence,
            )
        )

        if (
            invoice.status
            == InvoiceStatus.PAID
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Project deposit "
                    "has already been paid."
                ),
            )

        connection.commit()

        public_app_url = os.getenv(
            "RA_PUBLIC_APP_URL",
            "http://localhost:3000",
        ).rstrip("/")

        success_url = (
            f"{public_app_url}"
            f"/quote/{token}"
            "?payment=success"
        )

        cancel_url = (
            f"{public_app_url}"
            f"/quote/{token}"
            "?payment=cancelled"
        )

        session = (
            create_deposit_checkout_session(
                quote=quote,
                invoice=invoice,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        )

    except HTTPException:
        raise

    except StripeConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to create "
                "Stripe Checkout session: "
                f"{type(exc).__name__}"
            ),
        ) from exc

    if not session.url:
        raise HTTPException(
            status_code=502,
            detail=(
                "Stripe did not return "
                "a Checkout URL."
            ),
        )

    return CheckoutResponse(
        checkout_url=session.url,
        session_id=session.id,
        invoice_number=(
            invoice.invoice_number
        ),
        amount=str(
            invoice.total
        ),
    )


@router.get(
    "/quotes/public/{token}/payment-status",
    response_model=DepositStatusResponse,
)
def get_quote_payment_status(
    token: str,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteQuoteRepository(
        connection
    )

    quote = (
        repository
        .get_by_public_token_hash(
            hash_public_token(token)
        )
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found.",
        )

    deposit = get_deposit_line(
        quote
    )

    if deposit is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Quote does not contain "
                "a project deposit."
            ),
        )

    persistence = (
        SQLitePaymentPersistence(
            connection
        )
    )

    invoice = (
        persistence
        .get_deposit_invoice_for_quote(
            quote.id
        )
    )

    if invoice is None:
        return DepositStatusResponse(
            deposit_amount=str(
                deposit.amount
            ),
            invoice_number=None,
            invoice_status=None,
            amount_paid="0.00",
            balance_due=str(
                deposit.amount
            ),
            deposit_paid=False,
        )

    payments = (
        persistence
        .get_payments_for_invoice(
            invoice.id
        )
    )

    refresh_invoice(
        invoice=invoice,
        payments=payments,
    )

    return DepositStatusResponse(
        deposit_amount=str(
            invoice.total
        ),
        invoice_number=(
            invoice.invoice_number
        ),
        invoice_status=(
            invoice.status.value
        ),
        amount_paid=str(
            invoice.amount_paid
        ),
        balance_due=str(
            invoice.balance_due
        ),
        deposit_paid=(
            invoice.status
            == InvoiceStatus.PAID
        ),
    )


def process_paid_session(
    *,
    session,
    connection: sqlite3.Connection,
) -> None:
    metadata = (
        session.get("metadata")
        or {}
    )

    invoice_id_value = (
        metadata.get("invoice_id")
    )

    if not invoice_id_value:
        return

    persistence = (
        SQLitePaymentPersistence(
            connection
        )
    )

    session_id = session["id"]

    existing_payment = (
        persistence
        .get_payment_by_external_reference(
            session_id
        )
    )

    if existing_payment is not None:
        return

    invoice = (
        persistence.invoices.get(
            UUID(invoice_id_value)
        )
    )

    if invoice is None:
        raise RuntimeError(
            "Stripe payment references "
            "an unknown invoice."
        )

    amount_total = session.get(
        "amount_total"
    )

    if amount_total is None:
        raise RuntimeError(
            "Stripe payment is missing "
            "amount_total."
        )

    amount = (
        Decimal(str(amount_total))
        / Decimal("100")
    )

    if amount != invoice.total:
        raise RuntimeError(
            "Stripe payment amount "
            "does not match invoice total."
        )

    now = datetime.now(
        timezone.utc
    )

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        payment_method=(
            PaymentMethod.OTHER
        ),
        status=(
            PaymentStatus.RECEIVED
        ),
        external_reference=session_id,
        received_at=now,
    )

    persistence.add_payment(
        payment
    )

    payments = (
        persistence
        .get_payments_for_invoice(
            invoice.id
        )
    )

    invoice.updated_at = now

    refresh_invoice(
        invoice=invoice,
        payments=payments,
    )

    persistence.update_invoice(
        invoice
    )


@router.post(
    "/payments/stripe/webhook"
)
async def stripe_webhook(
    request: Request,
):
    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe signature "
                "is required."
            ),
        )

    try:
        event = construct_webhook_event(
            payload=payload,
            signature=signature,
        )

    except StripeConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe "
                "webhook signature."
            ),
        ) from exc

    event_type = event["type"]

    relevant_events = {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }

    # Acknowledge Stripe events that Paradigm Ra
    # does not need to process.
    if event_type not in relevant_events:
        return {
            "received": True,
        }

    session_object = (
        event["data"]["object"]
    )

    # stripe-python resources are StripeObject
    # instances, not normal dictionaries.
    if hasattr(
        session_object,
        "to_dict",
    ):
        session = (
            session_object.to_dict()
        )
    else:
        session = session_object

    if (
        event_type
        == "checkout.session.completed"
        and session.get(
            "payment_status"
        ) != "paid"
    ):
        return {
            "received": True,
        }

    # The webhook is async, so create SQLite
    # in this execution thread rather than
    # receiving a connection from FastAPI's
    # synchronous dependency thread.
    connection = sqlite3.connect(
        get_database_path()
    )

    connection.row_factory = (
        sqlite3.Row
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    initialize_database(
        connection
    )

    try:
        process_paid_session(
            session=session,
            connection=connection,
        )

        connection.commit()

    except Exception as exc:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process "
                "Stripe payment: "
                f"{type(exc).__name__}"
            ),
        ) from exc

    finally:
        connection.close()

    return {
        "received": True,
    }
