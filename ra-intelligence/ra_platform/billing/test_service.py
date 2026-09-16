from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from .models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
    TimeEntry,
    TimeEntryStatus,
)

from .service import (
    generate_invoice_from_time_entries,
)


def build_brewbird_terms(engagement_id):
    return [
        EngagementBillingTerms(
            engagement_id=engagement_id,
            billing_type=BillingType.HOURLY,
            billing_cadence=BillingCadence.WEEKLY,
            hourly_rate=Decimal("70.00"),
            expected_hours_min=Decimal("15"),
            expected_hours_max=Decimal("30"),
            payment_terms_days=30,
            effective_from=date(2026, 9, 15),
        )
    ]


def test_brewbird_invoice_generation():
    engagement_id = uuid4()
    client_organization_id = uuid4()

    time_entries = [
        TimeEntry(
            engagement_id=engagement_id,
            work_date=date(2026, 9, 15),
            description="Bank reconciliation",
            hours=Decimal("3.5"),
            status=TimeEntryStatus.APPROVED,
        ),
        TimeEntry(
            engagement_id=engagement_id,
            work_date=date(2026, 9, 16),
            description="Vendor and AP review",
            hours=Decimal("4"),
            status=TimeEntryStatus.APPROVED,
        ),
        TimeEntry(
            engagement_id=engagement_id,
            work_date=date(2026, 9, 17),
            description="Monthly bookkeeping",
            hours=Decimal("5"),
            status=TimeEntryStatus.APPROVED,
        ),
    ]

    invoice = generate_invoice_from_time_entries(
        client_organization_id=client_organization_id,
        invoice_number="RA-2026-001",
        time_entries=time_entries,
        billing_terms=build_brewbird_terms(
            engagement_id
        ),
        bill_to_name="BrewBird Coffee",
        issue_date=date(2026, 9, 30),
    )

    assert invoice.subtotal == Decimal("875.00")
    assert invoice.total == Decimal("875.00")
    assert invoice.amount_paid == Decimal("0.00")
    assert invoice.balance_due == Decimal("875.00")


def test_time_entry_before_billing_terms_raises_error():
    engagement_id = uuid4()
    client_organization_id = uuid4()

    time_entries = [
        TimeEntry(
            engagement_id=engagement_id,
            work_date=date(2026, 9, 10),
            description="Bookkeeping services",
            hours=Decimal("2"),
            status=TimeEntryStatus.APPROVED,
        )
    ]

    with pytest.raises(ValueError):
        generate_invoice_from_time_entries(
            client_organization_id=client_organization_id,
            invoice_number="RA-2026-002",
            time_entries=time_entries,
            billing_terms=build_brewbird_terms(
                engagement_id
            ),
            bill_to_name="BrewBird Coffee",
            issue_date=date(2026, 9, 30),
        )
