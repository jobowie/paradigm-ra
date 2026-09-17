from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter

from ra_platform.billing.models import (
    Quote,
    QuoteLine,
)

from ra_platform.billing.service import (
    refresh_quote,
)


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
)


@router.get("/demo")
def get_demo_quote():
    quote = Quote(
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
        terms=(
            "50% deposit on acceptance. "
            "Remaining 50% due before launch. "
            "Two revision rounds included. "
            "Ongoing support is separate."
        ),
    )

    return refresh_quote(quote)