from __future__ import annotations

from discovery.core.flow import (
    finalize_flow,
    plan_flow,
)
from discovery.core.readiness import (
    evaluate_readiness,
)
from discovery.core.reconcile import (
    reconcile_state,
)
from discovery.models import (
    DiscoveryContact,
    DiscoveryState,
    DiscoveryTurnInput,
)
from discovery.providers.roles import (
    provider_for_role,
)


def test_completion_shuts_valve() -> None:
    state = DiscoveryState(
        primary_problem=(
            "Manual production reporting "
            "delays leadership visibility."
        ),
        current_process=(
            "Supervisors complete spreadsheets "
            "and operations consolidates them."
        ),
        current_systems=[
            "Microsoft 365",
            "SQL Server",
        ],
        pain_points=[
            "Manual consolidation",
            "Delayed reporting",
        ],
        desired_outcomes=[
            "Near-real-time production reporting"
        ],
        users_or_teams_affected=[
            "Supervisors",
            "Operations",
            "Leadership",
        ],
        timeline="Within three months",
        decision_process=(
            "Taylor leads the project and "
            "the COO approves budget."
        ),
    )

    decision = evaluate_readiness(
        state
    )

    assert decision.complete is True

    turn = DiscoveryTurnInput(
        contact=DiscoveryContact(
            first_name="Taylor",
            company="Crestview Manufacturing",
            email="test@example.com",
        ),
        latest_prospect_message=(
            "Anything else you need?"
        ),
        current_state=state.model_dump(),
    )

    plan = plan_flow(turn)

    assert plan.route.role == "handoff"


def test_simple_gap_routes_rapid() -> None:
    turn = DiscoveryTurnInput(
        contact=DiscoveryContact(
            first_name="Dana",
            company="Westline Industrial",
            email="test@example.com",
        ),
        latest_prospect_message=(
            "We write phone orders down and "
            "enter them into QuickBooks later."
        ),
        current_state={},
    )

    plan = plan_flow(turn)

    assert plan.route.role == "rapid"


def test_complex_message_routes_complex() -> None:
    turn = DiscoveryTurnInput(
        contact=DiscoveryContact(
            first_name="Priya",
            company="Northstar Logistics",
            email="test@example.com",
        ),
        latest_prospect_message=(
            "We need to modernize a legacy "
            "internal application used by several "
            "departments without disrupting "
            "business-critical operations."
        ),
        current_state={},
    )

    plan = plan_flow(turn)

    assert plan.route.role == "complex"


def test_reconcile_preserves_known_truth() -> None:
    prior = DiscoveryState(
        primary_problem="Slow quoting",
        timeline="Before January",
        service_category="automation",
        current_systems=[
            "Excel"
        ],
    )

    candidate = DiscoveryState(
        primary_problem="Slow quoting",
        service_category="unknown",
        current_systems=[
            "Email"
        ],
    )

    result = reconcile_state(
        prior,
        candidate,
    )

    assert (
        result.state.timeline
        == "Before January"
    )

    assert (
        result.state.service_category
        == "automation"
    )

    assert result.state.current_systems == [
        "Excel",
        "Email",
    ]


def test_postflight_can_close_valve() -> None:
    prior = DiscoveryState(
        primary_problem=(
            "Manual production reporting"
        ),
        current_process=(
            "Supervisors use spreadsheets"
        ),
        current_systems=[
            "Microsoft 365",
            "SQL Server",
        ],
        users_or_teams_affected=[
            "Operations",
            "Leadership",
        ],
    )

    candidate = DiscoveryState(
        primary_problem=(
            "Manual production reporting"
        ),
        current_process=(
            "Supervisors use spreadsheets"
        ),
        current_systems=[
            "Microsoft 365",
            "SQL Server",
        ],
        users_or_teams_affected=[
            "Operations",
            "Leadership",
        ],
        desired_outcomes=[
            "Near-real-time reporting"
        ],
        timeline="Within three months",
        decision_process=(
            "Project lead recommends; "
            "COO approves budget."
        ),
    )

    final = finalize_flow(
        prior,
        candidate,
    )

    assert final.readiness.complete is True
    assert final.state.missing_information == []


def test_provider_roles_are_isolated() -> None:
    assert (
        provider_for_role("rapid")
        == "mistral"
    )

    assert (
        provider_for_role("complex")
        == "openai"
    )

    assert (
        provider_for_role("handoff")
        is None
    )


def main() -> None:
    tests = [
        test_completion_shuts_valve,
        test_simple_gap_routes_rapid,
        test_complex_message_routes_complex,
        test_reconcile_preserves_known_truth,
        test_postflight_can_close_valve,
        test_provider_roles_are_isolated,
    ]

    for test in tests:
        test()

    print()
    print("RA FLOW CONTROL")
    print("----------------")
    print(
        f"Tests: {len(tests)}/{len(tests)} PASS"
    )
    print("Preflight valve:       PASS")
    print("Rapid routing:         PASS")
    print("Complex routing:       PASS")
    print("Canonical reconcile:   PASS")
    print("Postflight shutoff:    PASS")
    print("Provider isolation:    PASS")
    print()
    print("Ra controls the flow. ✓")
    print()


if __name__ == "__main__":
    main()
