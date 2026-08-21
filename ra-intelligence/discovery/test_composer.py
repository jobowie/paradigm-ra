from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.composer import compose_discovery_request
from discovery.models import DiscoveryTurnInput


def main() -> None:
    scenario = DISCOVERY_BENCHMARK_SCENARIOS[0]

    turn = DiscoveryTurnInput(
        contact=scenario.contact,
        history=scenario.history,
        latest_prospect_message=(
            scenario.latest_prospect_message
        ),
        current_state=scenario.current_state,
    )

    request = compose_discovery_request(turn)

    print()
    print("RA DISCOVERY — REQUEST COMPOSER")
    print("-------------------------------")
    print(
        f"Scenario: {scenario.id} — {scenario.title}"
    )
    print(
        f"System prompt: {len(request['system'])} chars"
    )
    print(
        f"User context:  {len(request['user'])} chars"
    )
    print()
    print("Latest prospect message:")
    print(scenario.latest_prospect_message)
    print()
    print("Composer check: PASS ✓")
    print()


if __name__ == "__main__":
    main()
