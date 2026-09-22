from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
)
from ra_platform.billing.terms_service import (
    BillingTermsValidationError,
    prepare_successor_billing_terms,
)


ENGAGEMENT_ID = uuid4()


def make_terms(
    *,
    effective_from: date,
    hourly_rate: (
        Decimal | None
    ) = Decimal("70.00"),
    expected_min: (
        Decimal | None
    ) = Decimal("15"),
    expected_max: (
        Decimal | None
    ) = Decimal("30"),
) -> EngagementBillingTerms:
    return EngagementBillingTerms(
        engagement_id=ENGAGEMENT_ID,
        billing_type=(
            BillingType.HOURLY
        ),
        billing_cadence=(
            BillingCadence.WEEKLY
        ),
        hourly_rate=hourly_rate,
        expected_hours_min=(
            expected_min
        ),
        expected_hours_max=(
            expected_max
        ),
        payment_terms_days=15,
        effective_from=(
            effective_from
        ),
    )


def test_first_terms_require_no_close():
    new_terms = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        )
    )

    closed, created = (
        prepare_successor_billing_terms(
            existing_terms=[],
            new_terms=new_terms,
        )
    )

    assert closed is None
    assert created is new_terms


def test_successor_closes_previous_day():
    previous = make_terms(
        effective_from=date(
            2026,
            9,
            1,
        )
    )

    successor = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        ),
        hourly_rate=(
            Decimal("80.00")
        ),
    )

    closed, created = (
        prepare_successor_billing_terms(
            existing_terms=[
                previous
            ],
            new_terms=successor,
        )
    )

    assert closed is previous

    assert (
        previous.effective_to
        == date(
            2026,
            9,
            21,
        )
    )

    assert created is successor


def test_same_day_successor_rejected():
    previous = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        )
    )

    successor = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        )
    )

    with pytest.raises(
        BillingTermsValidationError,
        match=(
            "must begin after "
            "the latest terms"
        ),
    ):
        prepare_successor_billing_terms(
            existing_terms=[
                previous
            ],
            new_terms=successor,
        )


def test_hourly_requires_rate():
    terms = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        ),
        hourly_rate=None,
    )

    with pytest.raises(
        BillingTermsValidationError,
        match=(
            "positive hourly rate"
        ),
    ):
        prepare_successor_billing_terms(
            existing_terms=[],
            new_terms=terms,
        )


def test_expected_max_cannot_be_below_min():
    terms = make_terms(
        effective_from=date(
            2026,
            9,
            22,
        ),
        expected_min=Decimal("30"),
        expected_max=Decimal("15"),
    )

    with pytest.raises(
        BillingTermsValidationError,
        match=(
            "cannot be below "
            "minimum hours"
        ),
    ):
        prepare_successor_billing_terms(
            existing_terms=[],
            new_terms=terms,
        )
