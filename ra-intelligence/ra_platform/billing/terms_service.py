from datetime import timedelta

from ra_platform.billing.models import (
    BillingType,
    EngagementBillingTerms,
)


class BillingTermsValidationError(
    ValueError
):
    pass


def validate_billing_terms(
    terms: EngagementBillingTerms,
) -> None:
    if (
        terms.billing_type
        == BillingType.HOURLY
        and (
            terms.hourly_rate
            is None
            or terms.hourly_rate <= 0
        )
    ):
        raise BillingTermsValidationError(
            "Hourly billing requires "
            "a positive hourly rate."
        )

    if (
        terms.expected_hours_min
        is not None
        and terms.expected_hours_max
        is not None
        and (
            terms.expected_hours_max
            < terms.expected_hours_min
        )
    ):
        raise BillingTermsValidationError(
            "Expected maximum hours "
            "cannot be below minimum hours."
        )


def prepare_successor_billing_terms(
    *,
    existing_terms: list[
        EngagementBillingTerms
    ],
    new_terms: EngagementBillingTerms,
) -> (
    tuple[
        EngagementBillingTerms | None,
        EngagementBillingTerms,
    ]
):
    validate_billing_terms(
        new_terms
    )

    if not existing_terms:
        return (
            None,
            new_terms,
        )

    ordered = sorted(
        existing_terms,
        key=lambda item:
            item.effective_from,
    )

    latest = ordered[-1]

    open_terms = [
        item
        for item in ordered
        if item.effective_to is None
    ]

    if len(open_terms) > 1:
        raise BillingTermsValidationError(
            "Multiple open billing terms "
            "exist for this engagement."
        )

    if (
        open_terms
        and open_terms[0].id
        != latest.id
    ):
        raise BillingTermsValidationError(
            "Billing terms history "
            "contains an invalid open range."
        )

    if (
        new_terms.effective_from
        <= latest.effective_from
    ):
        raise BillingTermsValidationError(
            "New billing terms must begin "
            "after the latest terms."
        )

    if (
        latest.effective_to
        is not None
        and new_terms.effective_from
        <= latest.effective_to
    ):
        raise BillingTermsValidationError(
            "Billing terms date ranges "
            "cannot overlap."
        )

    closed_terms = None

    if latest.effective_to is None:
        latest.effective_to = (
            new_terms.effective_from
            - timedelta(days=1)
        )

        closed_terms = latest

    return (
        closed_terms,
        new_terms,
    )
