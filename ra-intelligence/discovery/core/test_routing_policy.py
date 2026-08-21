from __future__ import annotations

from pathlib import Path

from discovery.core.models import (
    ReadinessDecision,
)
from discovery.core.routing import (
    choose_route,
    detect_signal_families,
)
from discovery.models import DiscoveryState


OPEN = ReadinessDecision(
    complete=False,
    score=0,
    gaps=["primary_problem"],
    reason="test",
)


def test_simple_automation_stays_rapid() -> None:
    state = DiscoveryState()

    route = choose_route(
        state,
        (
            "Customers call in orders and we "
            "write them down before entering "
            "them into QuickBooks."
        ),
        OPEN,
    )

    assert route.role == "rapid"


def test_rich_operational_turn_is_complex() -> None:
    message = (
        "We process about 150 orders a day across "
        "four locations. Customers order by phone "
        "or email, employees enter everything into "
        "QuickBooks Enterprise and update inventory "
        "manually. We want customers ordering online "
        "and orders flowing into our existing systems "
        "this quarter."
    )

    signals = detect_signal_families(
        message
    )

    assert "scale" in signals
    assert "systems" in signals
    assert "stakeholders" in signals
    assert "process_chain" in signals
    assert "future_state" in signals
    assert "timeline" in signals

    route = choose_route(
        DiscoveryState(),
        message,
        OPEN,
    )

    assert route.role == "complex"


def test_basic_integration_stays_rapid() -> None:
    route = choose_route(
        DiscoveryState(),
        (
            "Our CRM and accounting platform "
            "do not communicate, so customer "
            "information gets entered twice."
        ),
        OPEN,
    )

    assert route.role == "rapid"


def test_fragmented_advisory_is_complex() -> None:
    route = choose_route(
        DiscoveryState(),
        (
            "Different teams use different tools "
            "and we are not sure what we should "
            "replace versus connect."
        ),
        OPEN,
    )

    assert route.role == "complex"


def test_router_knows_no_provider_names() -> None:
    source = Path(
        "discovery/core/routing.py"
    ).read_text().casefold()

    assert "mistral" not in source
    assert "openai" not in source


def main() -> None:
    tests = [
        test_simple_automation_stays_rapid,
        test_rich_operational_turn_is_complex,
        test_basic_integration_stays_rapid,
        test_fragmented_advisory_is_complex,
        test_router_knows_no_provider_names,
    ]

    for test in tests:
        test()

    print()
    print("RA ROUTING POLICY")
    print("-----------------")
    print(
        f"Tests: {len(tests)}/{len(tests)} PASS"
    )
    print("Simple automation:      RAPID")
    print("Rich operational turn: COMPLEX")
    print("Basic integration:      RAPID")
    print("Fragmented advisory:    COMPLEX")
    print("Provider blindness:     PASS")
    print()
    print(
        "Ra measures information density, "
        "not verbosity. ✓"
    )
    print()


if __name__ == "__main__":
    main()
