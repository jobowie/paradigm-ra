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
