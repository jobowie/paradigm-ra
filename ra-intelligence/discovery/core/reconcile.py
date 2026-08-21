from __future__ import annotations

from discovery.core.models import (
    ReconciliationResult,
)
from discovery.models import DiscoveryState


TEXT_FIELDS = (
    "company_name",
    "contact_name",
    "website",
    "business_description",
    "primary_problem",
    "current_process",
    "business_impact",
    "urgency",
    "timeline",
    "budget_context",
    "decision_process",
)


LIST_FIELDS = (
    "current_systems",
    "pain_points",
    "desired_outcomes",
    "users_or_teams_affected",
    "integrations_needed",
    "requirements",
)


def _merge_list(
    prior: list[str],
    candidate: list[str],
) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()

    for item in [*prior, *candidate]:
        cleaned = item.strip()

        if not cleaned:
            continue

        key = cleaned.casefold()

        if key in seen:
            continue

        seen.add(key)
        output.append(cleaned)

    return output


def reconcile_state(
    prior_state: DiscoveryState,
    candidate_state: DiscoveryState,
) -> ReconciliationResult:
    """
    Lossless Ra state reconciliation.

    Provider output is a candidate interpretation.
    It does not directly become canonical truth.
    """

    data = prior_state.model_dump()

    preserved: list[str] = []
    updated: list[str] = []

    for field in TEXT_FIELDS:
        prior = getattr(prior_state, field)
        candidate = getattr(
            candidate_state,
            field,
        )

        if (
            candidate is not None
            and candidate.strip()
        ):
            data[field] = candidate

            if candidate != prior:
                updated.append(field)
        elif prior:
            preserved.append(field)

    for field in LIST_FIELDS:
        prior = getattr(prior_state, field)
        candidate = getattr(
            candidate_state,
            field,
        )

        merged = _merge_list(
            prior,
            candidate,
        )

        data[field] = merged

        if merged != prior:
            updated.append(field)
        elif prior:
            preserved.append(field)

    prior_service = (
        prior_state.service_category
    )
    candidate_service = (
        candidate_state.service_category
    )

    if (
        candidate_service == "unknown"
        and prior_service != "unknown"
    ):
        data["service_category"] = (
            prior_service
        )
        preserved.append(
            "service_category"
        )
    else:
        data["service_category"] = (
            candidate_service
        )

        if candidate_service != prior_service:
            updated.append(
                "service_category"
            )

    if candidate_state.qualification_score:
        data["qualification_score"] = (
            candidate_state.qualification_score
        )
    else:
        data["qualification_score"] = (
            prior_state.qualification_score
        )

    if candidate_state.missing_information:
        data["missing_information"] = (
            candidate_state.missing_information
        )
    else:
        data["missing_information"] = (
            prior_state.missing_information
        )

    state = DiscoveryState.model_validate(
        data
    )

    return ReconciliationResult(
        state=state,
        preserved_fields=sorted(
            set(preserved)
        ),
        updated_fields=sorted(
            set(updated)
        ),
    )
