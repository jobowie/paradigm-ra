from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from .models import (
    Quote,
    QuoteLine,
    QuoteStatus,
)

from .service import (
    accept_quote,
    refresh_quote,
    send_quote,
)


def build_strategic_crime_prevention_quote():
    return Quote(
        client_organization_id=uuid4(),
        engagement_id=uuid4(),
        quote_number="RA-Q-2026-001",
        issue_date=date(2026, 9, 16),
        expiration_date=date(2026, 9, 30),
        bill_to_name="Strategic Crime Prevention",
        line_items=[
            QuoteLine(
                description=(
                    "Website Design & Development"
                ),
                quantity=Decimal("1"),
                unit_rate=Decimal("750.00"),
            )
        ],
        notes=(
            "Production website based on the "
            "client-approved design concept."
        ),
        terms=(
            "50% deposit on acceptance. "
            "Remaining 50% due before launch. "
            "Two revision rounds included. "
            "Ongoing support is separate."
        ),
    )


def test_strategic_quote_total_is_server_calculated():
    quote = refresh_quote(
        build_strategic_crime_prevention_quote()
    )

    assert quote.subtotal == Decimal(
        "750.00"
    )

    assert quote.total == Decimal(
        "750.00"
    )

    assert quote.line_items[0].amount == Decimal(
        "750.00"
    )


def test_strategic_quote_can_be_sent_and_accepted():
    quote = refresh_quote(
        build_strategic_crime_prevention_quote()
    )

    sent_at = datetime(
        2026,
        9,
        16,
        15,
        0,
        tzinfo=timezone.utc,
    )

    accepted_at = datetime(
        2026,
        9,
        16,
        17,
        0,
        tzinfo=timezone.utc,
    )

    send_quote(
        quote,
        sent_at=sent_at,
    )

    assert quote.status == QuoteStatus.SENT
    assert quote.sent_at == sent_at

    accept_quote(
        quote,
        accepted_at=accepted_at,
    )

    assert (
        quote.status
        == QuoteStatus.ACCEPTED
    )

    assert quote.accepted_at == accepted_at


def test_draft_quote_cannot_be_accepted():
    quote = refresh_quote(
        build_strategic_crime_prevention_quote()
    )

    with pytest.raises(
        ValueError,
        match="Only sent quotes",
    ):
        accept_quote(quote)