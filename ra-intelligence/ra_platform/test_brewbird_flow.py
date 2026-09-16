from datetime import date
from decimal import Decimal

from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)

from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)

from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
    TimeEntry,
    TimeEntryStatus,
)

from ra_platform.billing.service import (
    generate_invoice_from_time_entries,
)


def test_brewbird_bookkeeping_production_flow():
    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )

    bookkeeping = Engagement(
        client_organization_id=brewbird.id,
        owner_organization_id=paradigm_ra.id,
        name="Bookkeeping",
        service_type="bookkeeping",
        source=EngagementSource.CONTRACT_CONVERSION,
        status=EngagementStatus.ACTIVE,
    )

    billing_terms = [
        EngagementBillingTerms(
            engagement_id=bookkeeping.id,
            billing_type=BillingType.HOURLY,
            billing_cadence=BillingCadence.WEEKLY,
            hourly_rate=Decimal("70.00"),
            expected_hours_min=Decimal("15"),
            expected_hours_max=Decimal("30"),
            payment_terms_days=30,
            effective_from=date(2026, 9, 15),
        )
    ]

    time_entries = [
        TimeEntry(
            engagement_id=bookkeeping.id,
            work_date=date(2026, 9, 15),
            description="Bank reconciliation",
            hours=Decimal("5"),
            status=TimeEntryStatus.APPROVED,
        ),
        TimeEntry(
            engagement_id=bookkeeping.id,
            work_date=date(2026, 9, 16),
            description="Accounts payable review",
            hours=Decimal("6"),
            status=TimeEntryStatus.APPROVED,
        ),
        TimeEntry(
            engagement_id=bookkeeping.id,
            work_date=date(2026, 9, 17),
            description="Bookkeeping and ledger review",
            hours=Decimal("9"),
            status=TimeEntryStatus.APPROVED,
        ),
    ]

    invoice = generate_invoice_from_time_entries(
        client_organization_id=brewbird.id,
        invoice_number="RA-2026-001",
        time_entries=time_entries,
        billing_terms=billing_terms,
        bill_to_name="BrewBird Coffee",
        issue_date=date(2026, 9, 30),
    )

    assert bookkeeping.client_organization_id == brewbird.id
    assert bookkeeping.owner_organization_id == paradigm_ra.id

    assert invoice.client_organization_id == brewbird.id

    assert len(invoice.line_items) == 3

    assert invoice.subtotal == Decimal("1400.00")
    assert invoice.total == Decimal("1400.00")
    assert invoice.amount_paid == Decimal("0.00")
    assert invoice.balance_due == Decimal("1400.00")

    for line in invoice.line_items:
        assert line.engagement_id == bookkeeping.id
        assert line.unit_rate == Decimal("70.00")
