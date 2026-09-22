import sqlite3

import pytest

from ra_platform.billing.models import (
    TimeEntry,
    TimeEntryFriction,
    TimeEntryStatus,
    TimeEntryWorkstream,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
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


def build_fixture():
    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = sqlite3.Row

    initialize_database(
        connection
    )

    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    owner = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    client = Organization(
        name="Internal Test",
        type=OrganizationType.CLIENT,
    )

    organizations.add(owner)
    organizations.add(client)

    engagement = Engagement(
        client_organization_id=client.id,
        owner_organization_id=owner.id,
        name="Test Engagement",
        service_type="bookkeeping",
        source=EngagementSource.DIRECT,
    )

    SQLiteEngagementRepository(
        connection
    ).add(
        engagement
    )

    entry = TimeEntry(
        engagement_id=engagement.id,
        work_date="2026-09-22",
        description="Initial work",
        hours="1.00",
    )

    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    repository.add_many(
        [entry]
    )

    connection.commit()

    return (
        connection,
        repository,
        entry,
    )


def test_draft_time_entry_can_be_edited():
    (
        connection,
        repository,
        entry,
    ) = build_fixture()

    entry.description = (
        "Bank reconciliation"
    )

    entry.hours = "1.50"

    entry.workstream = (
        TimeEntryWorkstream.RECONCILIATION
    )

    entry.friction = (
        TimeEntryFriction.MISSING_INFORMATION
    )

    entry.operational_note = (
        "Waiting on source document."
    )

    repository.update_draft(
        entry
    )

    connection.commit()

    loaded = repository.get(
        entry.id
    )

    assert loaded is not None

    assert (
        loaded.description
        == "Bank reconciliation"
    )

    assert str(
        loaded.hours
    ) == "1.50"

    assert (
        loaded.workstream
        == TimeEntryWorkstream.RECONCILIATION
    )

    assert (
        loaded.friction
        == TimeEntryFriction.MISSING_INFORMATION
    )

    assert (
        loaded.operational_note
        == "Waiting on source document."
    )


def test_approved_time_entry_cannot_be_edited():
    (
        _connection,
        repository,
        entry,
    ) = build_fixture()

    entry.status = (
        TimeEntryStatus.APPROVED
    )

    with pytest.raises(
        ValueError,
        match=(
            "Only draft time entries "
            "can be edited."
        ),
    ):
        repository.update_draft(
            entry
        )
