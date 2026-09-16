import sqlite3

from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)

from .sqlite import initialize_database

from .sqlite_repositories import (
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
)

from ra_platform.billing.models import (
    Quote,
    QuoteLine,
    QuoteStatus,
)

from ra_platform.billing.service import (
    refresh_quote,
)

from .sqlite_repositories import (
    SQLiteQuoteRepository,
)


EXPECTED_TABLES = {
    "organizations",
    "engagements",
    "engagement_billing_terms",
    "invoices",
    "invoice_lines",
    "time_entries",
    "invoice_line_time_entries",
    "payments",
}


def build_memory_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    initialize_database(connection)

    return connection


def test_database_schema_can_be_initialized():
    connection = build_memory_database()

    tables = {
        row[0]
        for row in connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )
    }

    assert EXPECTED_TABLES.issubset(tables)


def test_foreign_keys_are_enforced():
    connection = build_memory_database()

    try:
        connection.execute(
            """
            INSERT INTO engagements (
                id,
                client_organization_id,
                owner_organization_id,
                name,
                service_type,
                source,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "engagement-1",
                "missing-client",
                "missing-owner",
                "Bookkeeping",
                "bookkeeping",
                "contract_conversion",
                "active",
                "2026-09-15T00:00:00+00:00",
                "2026-09-15T00:00:00+00:00",
            ),
        )

        connection.commit()

        assert False, "Expected foreign-key failure"

    except sqlite3.IntegrityError:
        pass


def test_brewbird_organization_and_engagement_round_trip():
    connection = build_memory_database()

    organizations = SQLiteOrganizationRepository(
        connection
    )
    engagements = SQLiteEngagementRepository(
        connection
    )

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )

    organizations.add(paradigm_ra)
    organizations.add(brewbird)

    bookkeeping = Engagement(
        client_organization_id=brewbird.id,
        owner_organization_id=paradigm_ra.id,
        name="Bookkeeping",
        service_type="bookkeeping",
        source=EngagementSource.CONTRACT_CONVERSION,
        status=EngagementStatus.ACTIVE,
    )

    engagements.add(bookkeeping)

    connection.commit()

    saved_brewbird = organizations.get(
        brewbird.id
    )
    saved_engagement = engagements.get(
        bookkeeping.id
    )

    assert saved_brewbird is not None
    assert saved_brewbird.id == brewbird.id
    assert saved_brewbird.name == "BrewBird Coffee"

    assert saved_engagement is not None

    assert (
        saved_engagement.client_organization_id
        == brewbird.id
    )

    assert (
        saved_engagement.owner_organization_id
        == paradigm_ra.id
    )

    assert (
        saved_engagement.source
        == EngagementSource.CONTRACT_CONVERSION
    )

from datetime import date
from decimal import Decimal

from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
    TimeEntry,
    TimeEntryStatus,
)

from ra_platform.billing.service import (
    create_invoice_from_time_entries,
)

from .sqlite_repositories import (
    SQLiteBillingUnitOfWork,
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
    SQLiteTimeEntryRepository,
)

def test_brewbird_invoice_transaction_round_trip():
    connection = build_memory_database()

    organizations = SQLiteOrganizationRepository(
        connection
    )
    engagements = SQLiteEngagementRepository(
        connection
    )
    time_entry_repository = SQLiteTimeEntryRepository(
        connection
    )

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )

    organizations.add(paradigm_ra)
    organizations.add(brewbird)

    bookkeeping = Engagement(
        client_organization_id=brewbird.id,
        owner_organization_id=paradigm_ra.id,
        name="Bookkeeping",
        service_type="bookkeeping",
        source=EngagementSource.CONTRACT_CONVERSION,
        status=EngagementStatus.ACTIVE,
    )

    engagements.add(bookkeeping)

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
    ]

    time_entry_repository.add_many(
        time_entries
    )

    connection.commit()

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

    uow = SQLiteBillingUnitOfWork(
        connection
    )

    invoice = create_invoice_from_time_entries(
        uow=uow,
        client_organization_id=brewbird.id,
        invoice_number="RA-2026-001",
        time_entries=time_entries,
        billing_terms=billing_terms,
        bill_to_name="BrewBird Coffee",
        issue_date=date(2026, 9, 30),
    )

    saved_invoice = uow.invoices.get(
        invoice.id
    )

    saved_entry_one = uow.time_entries.get(
        time_entries[0].id
    )

    saved_entry_two = uow.time_entries.get(
        time_entries[1].id
    )

    assert saved_invoice is not None
    assert saved_invoice.total == Decimal(
        "770.00"
    )

    assert len(
        saved_invoice.line_items
    ) == 2

    assert saved_entry_one is not None
    assert saved_entry_two is not None

    assert (
        saved_entry_one.status
        == TimeEntryStatus.INVOICED
    )

    assert (
        saved_entry_two.status
        == TimeEntryStatus.INVOICED
    )

    assert (
        saved_entry_one.invoice_id
        == invoice.id
    )

    assert (
        saved_entry_two.invoice_id
        == invoice.id
    )

def test_strategic_quote_round_trip_and_client_isolation():
    connection = build_memory_database()

    organizations = SQLiteOrganizationRepository(
        connection
    )
    engagements = SQLiteEngagementRepository(
        connection
    )
    quotes = SQLiteQuoteRepository(
        connection
    )

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    strategic = Organization(
        name="Strategic Crime Prevention",
        type=OrganizationType.CLIENT,
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )

    organizations.add(paradigm_ra)
    organizations.add(strategic)
    organizations.add(brewbird)

    website_engagement = Engagement(
        client_organization_id=strategic.id,
        owner_organization_id=paradigm_ra.id,
        name="Website Design & Development",
        service_type="website_design_development",
        source=EngagementSource.DIRECT,
        status=EngagementStatus.ACTIVE,
    )

    engagements.add(website_engagement)

    quote = Quote(
        client_organization_id=strategic.id,
        engagement_id=website_engagement.id,
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

    refresh_quote(quote)

    quotes.add(quote)

    connection.commit()

    saved_quote = quotes.get_for_client(
        quote.id,
        strategic.id,
    )

    assert saved_quote is not None
    assert saved_quote.id == quote.id
    assert saved_quote.total == Decimal("750.00")
    assert saved_quote.client_organization_id == strategic.id
    assert saved_quote.engagement_id == website_engagement.id
    assert len(saved_quote.line_items) == 1

    brewbird_attempt = quotes.get_for_client(
        quote.id,
        brewbird.id,
    )

    assert brewbird_attempt is None