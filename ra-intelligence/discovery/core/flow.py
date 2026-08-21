from __future__ import annotations

from discovery.core.models import (
    FlowFinalization,
    FlowPlan,
)
from discovery.core.readiness import (
    evaluate_readiness,
)
from discovery.core.reconcile import (
    reconcile_state,
)
from discovery.core.routing import (
    choose_route,
)
from discovery.models import (
    DiscoveryState,
    DiscoveryTurnInput,
)


def plan_flow(
    turn: DiscoveryTurnInput,
) -> FlowPlan:
    """
    Ra intake valve.

    Evaluate canonical state BEFORE allowing a model call.
    """

    state = DiscoveryState.model_validate(
        turn.current_state or {}
    )

    # Contact was already captured by Paradigm Ra.
    # Do not make a model rediscover known form data.
    contact_updates: dict[str, str] = {}

    if not state.contact_name:
        contact_updates["contact_name"] = (
            turn.contact.first_name
        )

    if not state.company_name:
        contact_updates["company_name"] = (
            turn.contact.company
        )

    if contact_updates:
        state = state.model_copy(
            update=contact_updates
        )

    readiness = evaluate_readiness(
        state
    )

    route = choose_route(
        state=state,
        latest_message=(
            turn.latest_prospect_message
        ),
        readiness=readiness,
    )

    return FlowPlan(
        state=state,
        readiness=readiness,
        route=route,
    )


def finalize_flow(
    prior_state: DiscoveryState,
    candidate_state: DiscoveryState,
) -> FlowFinalization:
    """
    Ra output valve.

    Reconcile provider interpretation, then independently
    calculate discovery readiness.
    """

    reconciled = reconcile_state(
        prior_state,
        candidate_state,
    )

    readiness = evaluate_readiness(
        reconciled.state
    )

    # These values are Ra-owned.
    final_state = reconciled.state.model_copy(
        update={
            "qualification_score": (
                readiness.score
            ),
            "missing_information": (
                []
                if readiness.complete
                else readiness.gaps
            ),
        }
    )

    return FlowFinalization(
        state=final_state,
        readiness=readiness,
        preserved_fields=(
            reconciled.preserved_fields
        ),
        updated_fields=(
            reconciled.updated_fields
        ),
    )
