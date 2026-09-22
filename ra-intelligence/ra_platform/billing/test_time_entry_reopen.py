from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from ra_platform.billing.models import (
    TimeEntry,
    TimeEntryStatus,
)
from ra_platform.billing.service import (
    reopen_time_entry,
)


def make_entry(
    status: TimeEntryStatus,
) -> TimeEntry:
    return TimeEntry(
        engagement_id=uuid4(),
        work_date=date(
            2026,
            9,
            22,
        ),
        description="Reconciliation",
        hours=Decimal("1.00"),
        status=status,
    )


def test_approved_entry_reopens_as_draft():
    entry = make_entry(
        TimeEntryStatus.APPROVED
    )

    reopened = reopen_time_entry(
        entry
    )

    assert (
        reopened.status
        == TimeEntryStatus.DRAFT
    )

    assert reopened.id == entry.id


def test_draft_entry_cannot_be_reopened():
    entry = make_entry(
        TimeEntryStatus.DRAFT
    )

    with pytest.raises(
        ValueError,
        match=(
            "Only approved time entries "
            "can be reopened."
        ),
    ):
        reopen_time_entry(
            entry
        )


def test_invoiced_entry_cannot_be_reopened():
    entry = make_entry(
        TimeEntryStatus.INVOICED
    )

    entry.invoice_id = uuid4()

    with pytest.raises(
        ValueError,
        match=(
            "Invoiced time entries "
            "cannot be reopened."
        ),
    ):
        reopen_time_entry(
            entry
        )
