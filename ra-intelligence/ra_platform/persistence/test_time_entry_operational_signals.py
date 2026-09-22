import sqlite3

from datetime import date
from decimal import Decimal

from ra_platform.billing.models import (
    TimeEntry,
    TimeEntryFriction,
    TimeEntryWorkstream,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
    SQLiteTimeEntryRepository,
)


def make_connection():
    connection = sqlite3.connect(
        ":memory:"
    )
    connection.row_factory = sqlite3.Row

    initialize_database(
        connection
    )

    return connection


def test_time_entry_operational_signals_round_trip():
    connection = make_connection()

    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=(
            OrganizationType
            .PARADIGM_RA
        ),
    )

    client = Organization(
        name="Operational Signal Test",
        type=(
            OrganizationType.CLIENT
        ),
    )

    organizations.add(
        paradigm_ra
    )

    organizations.add(
        client
    )

    engagement = Engagement(
        client_organization_id=(
            client.id
        ),
        owner_organization_id=(
            paradigm_ra.id
        ),
        name="Bookkeeping",
        service_type="bookkeeping",
        source=(
            EngagementSource.DIRECT
        ),
        status=(
            EngagementStatus.ACTIVE
        ),
    )

    SQLiteEngagementRepository(
        connection
    ).add(
        engagement
    )

    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    unknown_friction = TimeEntry(
        engagement_id=engagement.id,
        work_date=date(
            2026,
            9,
            21,
        ),
        description=(
            "Reconciliation review"
        ),
        hours=Decimal("1.25"),
        workstream=(
            TimeEntryWorkstream
            .RECONCILIATION
        ),
        friction=None,
        operational_note=None,
    )

    explicit_none = TimeEntry(
        engagement_id=engagement.id,
        work_date=date(
            2026,
            9,
            21,
        ),
        description=(
            "Accounts payable review"
        ),
        hours=Decimal("0.75"),
        workstream=(
            TimeEntryWorkstream
            .ACCOUNTS_PAYABLE
        ),
        friction=(
            TimeEntryFriction
            .NONE_OBSERVED
        ),
        operational_note=(
            "Workflow completed "
            "without observed friction."
        ),
    )

    repository.add_many(
        [
            unknown_friction,
            explicit_none,
        ]
    )

    connection.commit()

    loaded_unknown = repository.get(
        unknown_friction.id
    )

    loaded_none = repository.get(
        explicit_none.id
    )

    assert loaded_unknown is not None

    assert loaded_unknown.workstream == (
        TimeEntryWorkstream
        .RECONCILIATION
    )

    assert loaded_unknown.friction is None

    assert (
        loaded_unknown.operational_note
        is None
    )

    assert loaded_none is not None

    assert loaded_none.workstream == (
        TimeEntryWorkstream
        .ACCOUNTS_PAYABLE
    )

    assert loaded_none.friction == (
        TimeEntryFriction
        .NONE_OBSERVED
    )

    assert loaded_none.operational_note == (
        "Workflow completed without "
        "observed friction."
    )

    listed = (
        repository.list_for_engagement(
            engagement.id
        )
    )

    assert len(listed) == 2

    connection.close()
